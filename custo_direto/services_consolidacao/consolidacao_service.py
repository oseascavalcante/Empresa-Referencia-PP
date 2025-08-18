from decimal import Decimal
from django.db.models import Sum, F, Q
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from ..models import (
    CustoDiretoFuncao, 
    ConsolidacaoCustoContrato, 
    ConsolidacaoCustoRegional,
    ConsolidacaoCustoPeriodo
)
from cad_contrato.models import CadastroContrato
from cadastro_equipe.models import ComposicaoEquipe
import logging

logger = logging.getLogger(__name__)


class ConsolidacaoService:
    """
    Service avançado para consolidação de custos diretos.
    Implementa estratégias de cache, consolidação incremental e materialização.
    """
    
    CACHE_TTL = 3600  # 1 hora
    
    @classmethod
    def consolidar_contrato(cls, contrato_id, force_refresh=False):
        """
        Consolida todos os custos de um contrato.
        
        Args:
            contrato_id: ID do contrato
            force_refresh: Força recálculo ignorando cache
            
        Returns:
            ConsolidacaoCustoContrato: Instância consolidada
        """
        cache_key = f"consolidacao_contrato_{contrato_id}"
        
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Retornando consolidação do cache para contrato {contrato_id}")
                return cached_result
        
        try:
            with transaction.atomic():
                contrato = CadastroContrato.objects.get(contrato=contrato_id)
                
                # Buscar ou criar consolidação
                consolidacao, created = ConsolidacaoCustoContrato.objects.get_or_create(
                    contrato=contrato,
                    defaults={'versao_calculo': '2.0'}
                )
                
                # Executar consolidação
                consolidacao.consolidar()
                consolidacao.save()
                
                # Cache por 1 hora
                cache.set(cache_key, consolidacao, cls.CACHE_TTL)
                
                logger.info(f"Consolidação {'criada' if created else 'atualizada'} para contrato {contrato_id}")
                return consolidacao
                
        except Exception as e:
            logger.error(f"Erro ao consolidar contrato {contrato_id}: {e}")
            raise
    
    @classmethod
    def consolidar_todas_regionais(cls, contrato_id, force_refresh=False):
        """
        Consolida custos por todas as regionais de um contrato.
        
        Args:
            contrato_id: ID do contrato
            force_refresh: Força recálculo ignorando cache
            
        Returns:
            List[ConsolidacaoCustoRegional]: Lista de consolidações regionais
        """
        cache_key = f"consolidacao_regionais_{contrato_id}"
        
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        try:
            contrato = CadastroContrato.objects.get(contrato=contrato_id)
            regionais = contrato.regionais.all()
            consolidacoes = []
            
            for regional in regionais:
                consolidacao = cls._consolidar_regional(contrato, regional)
                consolidacoes.append(consolidacao)
            
            # Cache por 1 hora
            cache.set(cache_key, consolidacoes, cls.CACHE_TTL)
            
            return consolidacoes
            
        except Exception as e:
            logger.error(f"Erro ao consolidar regionais do contrato {contrato_id}: {e}")
            raise
    
    @classmethod
    def _consolidar_regional(cls, contrato, regional):
        """
        Consolida custos de uma regional específica.
        """
        consolidacao, created = ConsolidacaoCustoRegional.objects.get_or_create(
            contrato=contrato,
            regional=regional
        )
        
        # Agregação por regional usando Django ORM
        custos = CustoDiretoFuncao.objects.filter(
            contrato=contrato,
            regional=regional
        ).aggregate(
            total_mao_obra=Sum('custo_total') or Decimal('0.00'),
            total_veiculos=Sum('custo_veiculos') or Decimal('0.00'),
            total_combustivel=Sum('custo_combustivel') or Decimal('0.00'),
            total_equipamentos=Sum(
                F('custo_epi') + F('custo_epc') + F('custo_ferramentas') +
                F('custo_equipamentos_ti') + F('custo_despesas_ti') + 
                F('custo_materiais_consumo') + F('custo_despesas_diversas')
            ) or Decimal('0.00'),
            total_funcionarios=Sum('quantidade_total_funcionarios') or 0
        )
        
        # Atualizar consolidação
        consolidacao.custo_mao_obra = custos['total_mao_obra']
        consolidacao.custo_veiculos = custos['total_veiculos']
        consolidacao.custo_combustivel = custos['total_combustivel']
        consolidacao.custo_equipamentos = custos['total_equipamentos']
        consolidacao.custo_total = (
            consolidacao.custo_mao_obra + consolidacao.custo_veiculos +
            consolidacao.custo_combustivel + consolidacao.custo_equipamentos
        )
        consolidacao.total_funcionarios = custos['total_funcionarios']
        
        # Total de equipes na regional
        total_equipes = ComposicaoEquipe.objects.filter(
            contrato=contrato,
            regional=regional
        ).aggregate(
            total=Sum('quantidade_equipes')
        )['total'] or Decimal('0.00')
        
        consolidacao.total_equipes = total_equipes
        consolidacao.save()
        
        return consolidacao
    
    @classmethod
    def consolidar_periodo(cls, contrato_id, ano, mes=None, tipo_periodo='MENSAL'):
        """
        Consolida custos por período específico.
        
        Args:
            contrato_id: ID do contrato
            ano: Ano do período
            mes: Mês (para consolidação mensal)
            tipo_periodo: Tipo do período (MENSAL, TRIMESTRAL, ANUAL)
        """
        try:
            contrato = CadastroContrato.objects.get(contrato=contrato_id)
            
            # Definir filtros temporais baseados no período
            filtros_data = cls._get_filtros_periodo(ano, mes, tipo_periodo)
            
            consolidacao, created = ConsolidacaoCustoPeriodo.objects.get_or_create(
                contrato=contrato,
                tipo_periodo=tipo_periodo,
                ano=ano,
                mes=mes,
                defaults={'trimestre': cls._get_trimestre(mes) if tipo_periodo == 'TRIMESTRAL' else None}
            )
            
            # Agregar custos do período
            custos = CustoDiretoFuncao.objects.filter(
                contrato=contrato,
                **filtros_data
            ).aggregate(
                total_mao_obra=Sum('custo_total') or Decimal('0.00'),
                total_veiculos=Sum('custo_veiculos') or Decimal('0.00'),
                total_combustivel=Sum('custo_combustivel') or Decimal('0.00'),
                total_equipamentos=Sum(
                    F('custo_epi') + F('custo_epc') + F('custo_ferramentas') +
                    F('custo_equipamentos_ti') + F('custo_despesas_ti') + 
                    F('custo_materiais_consumo') + F('custo_despesas_diversas')
                ) or Decimal('0.00')
            )
            
            # Atualizar consolidação
            consolidacao.custo_mao_obra = custos['total_mao_obra']
            consolidacao.custo_veiculos = custos['total_veiculos']
            consolidacao.custo_combustivel = custos['total_combustivel']
            consolidacao.custo_equipamentos = custos['total_equipamentos']
            consolidacao.custo_total = sum(custos.values())
            consolidacao.save()
            
            return consolidacao
            
        except Exception as e:
            logger.error(f"Erro ao consolidar período {ano}/{mes} do contrato {contrato_id}: {e}")
            raise
    
    @classmethod
    def _get_filtros_periodo(cls, ano, mes, tipo_periodo):
        """
        Retorna filtros de data baseados no tipo de período.
        """
        if tipo_periodo == 'MENSAL' and mes:
            return {
                'created_at__year': ano,
                'created_at__month': mes
            }
        elif tipo_periodo == 'ANUAL':
            return {
                'created_at__year': ano
            }
        elif tipo_periodo == 'TRIMESTRAL':
            trimestre = cls._get_trimestre(mes)
            meses_trimestre = cls._get_meses_trimestre(trimestre)
            return {
                'created_at__year': ano,
                'created_at__month__in': meses_trimestre
            }
        
        return {}
    
    @classmethod
    def _get_trimestre(cls, mes):
        """Retorna o trimestre baseado no mês."""
        if not mes:
            return None
        return ((mes - 1) // 3) + 1
    
    @classmethod
    def _get_meses_trimestre(cls, trimestre):
        """Retorna os meses de um trimestre."""
        meses_por_trimestre = {
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }
        return meses_por_trimestre.get(trimestre, [])
    
    @classmethod
    def invalidar_cache_contrato(cls, contrato_id):
        """
        Invalida todo o cache relacionado a um contrato.
        """
        cache_keys = [
            f"consolidacao_contrato_{contrato_id}",
            f"consolidacao_regionais_{contrato_id}",
            f"dashboard_custos_{contrato_id}",
            f"analytics_contrato_{contrato_id}"
        ]
        
        cache.delete_many(cache_keys)
        logger.info(f"Cache invalidado para contrato {contrato_id}")
    
    @classmethod
    def obter_resumo_completo(cls, contrato_id):
        """
        Retorna um resumo completo de todos os custos do contrato.
        Utiliza agregações Django para máxima performance.
        """
        cache_key = f"resumo_completo_{contrato_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            contrato = CadastroContrato.objects.get(contrato=contrato_id)
            
            # Usar managers customizados para otimização
            resumo = {
                'contrato': cls.consolidar_contrato(contrato_id),
                'por_regional': CustoDiretoFuncao.objects.consolidacao_por_regional(contrato_id),
                'por_escopo': CustoDiretoFuncao.objects.consolidacao_por_escopo(contrato_id),
                'por_equipe': CustoDiretoFuncao.objects.consolidacao_por_equipe(contrato_id),
                'top_custos': CustoDiretoFuncao.objects.top_custos_por_funcao(contrato_id, 10),
                'encargos_sociais': CustoDiretoFuncao.objects.resumo_encargos_sociais(contrato_id),
                'timestamp': timezone.now()
            }
            
            # Cache por 30 minutos
            cache.set(cache_key, resumo, 1800)
            
            return resumo
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo completo do contrato {contrato_id}: {e}")
            raise
    
    @classmethod
    def recalcular_tudo_incremental(cls, contrato_id):
        """
        Recálculo incremental inteligente baseado em timestamps.
        Apenas recalcula o que realmente mudou.
        """
        try:
            # Buscar última consolidação
            ultima_consolidacao = ConsolidacaoCustoContrato.objects.filter(
                contrato__contrato=contrato_id
            ).first()
            
            if not ultima_consolidacao:
                # Primeira consolidação - calcular tudo
                return cls.consolidar_contrato(contrato_id, force_refresh=True)
            
            # Verificar se há mudanças desde a última consolidação
            ultima_atualizacao = ultima_consolidacao.data_consolidacao
            
            mudancas_detectadas = CustoDiretoFuncao.objects.filter(
                contrato__contrato=contrato_id,
                updated_at__gt=ultima_atualizacao
            ).exists()
            
            if mudancas_detectadas:
                logger.info(f"Mudanças detectadas, recalculando contrato {contrato_id}")
                cls.invalidar_cache_contrato(contrato_id)
                return cls.consolidar_contrato(contrato_id, force_refresh=True)
            else:
                logger.info(f"Nenhuma mudança detectada para contrato {contrato_id}")
                return ultima_consolidacao
                
        except Exception as e:
            logger.error(f"Erro no recálculo incremental do contrato {contrato_id}: {e}")
            raise