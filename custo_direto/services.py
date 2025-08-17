from decimal import Decimal
from django.db.models import Sum, Q

from cadastro_equipe.models import FuncaoEquipe, ComposicaoEquipe, Equipe
from .models import CustoDiretoFuncao, CustoDireto
from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador
from cad_contrato.models import CadastroContrato
from equipamentos.models import EquipamentoEquipe, EquipamentoVidaUtil, EquipamentoMensal
import logging

logger = logging.getLogger(__name__)

def calcular_custo_funcao(funcao_equipe, contrato, encargos=None, beneficios=Decimal('0.00')):
    """
    Serviço para calcular o custo direto de uma função no contrato.
    """
    salario_base = funcao_equipe.salario
    quantidade_funcionarios = funcao_equipe.quantidade_funcionarios

    # Verifica se a quantidade de funcionários é maior que zero
    if quantidade_funcionarios <= 0:
        return None  # Não salva no banco de dados

    adicional_periculosidade = salario_base * Decimal('0.30') if funcao_equipe.periculosidade else Decimal('0')
    salario_hora = (salario_base + adicional_periculosidade) / Decimal('220')
    salario_hora_sem_periculosidade = salario_base / Decimal('220')

    valor_horas_extras_50 = salario_hora * Decimal('1.5') * funcao_equipe.horas_extras_50
    valor_horas_extras_100 = salario_hora * Decimal('2.0') * funcao_equipe.horas_extras_100
    
    valor_adicional_noturno = salario_hora_sem_periculosidade * Decimal('0.2') * Decimal('1.1428') * funcao_equipe.horas_adicional_noturno
    valor_prontidao = salario_hora_sem_periculosidade * funcao_equipe.horas_prontidao * Decimal('0.67')
    valor_sobreaviso = salario_hora_sem_periculosidade * funcao_equipe.horas_sobreaviso * Decimal('0.33')

    # Busca ou cria o custo direto da função
    custo_funcao, _ = CustoDiretoFuncao.objects.get_or_create(
        contrato=contrato,
        regional=funcao_equipe.composicao.regional,
        escopo=funcao_equipe.composicao.escopo,
        composicao=funcao_equipe.composicao,
        funcao=funcao_equipe.funcao,
        defaults={
            'quantidade_funcionarios': quantidade_funcionarios,
            'salario_base': salario_base
        }
    )

    # Atualiza os valores
    custo_funcao.quantidade_funcionarios = quantidade_funcionarios
    custo_funcao.salario_base = salario_base
    custo_funcao.adicional_periculosidade = adicional_periculosidade
    custo_funcao.valor_horas_extras_50 = valor_horas_extras_50
    custo_funcao.valor_horas_extras_100 = valor_horas_extras_100
    custo_funcao.valor_adicional_noturno = valor_adicional_noturno
    custo_funcao.valor_prontidao = valor_prontidao
    custo_funcao.valor_sobreaviso = valor_sobreaviso
    custo_funcao.outros_custos = funcao_equipe.outros_custos
    custo_funcao.beneficios = beneficios

    if encargos:
        custo_funcao.percentual_grupo_a = encargos.total_grupo_a
        custo_funcao.percentual_grupo_b = encargos.total_grupo_b
        custo_funcao.percentual_grupo_c = encargos.total_grupo_c
        custo_funcao.percentual_grupo_d = encargos.total_grupo_d
        custo_funcao.percentual_grupo_e = encargos.total_grupo_e

    custo_funcao.calcular_custo_total()
    custo_funcao.save()

    return custo_funcao


def recalcular_custo_contrato(contrato):
    """
    Recalcula os custos diretos por função vinculados ao contrato.
    Atualiza os registros de CustoDiretoFuncao com novos valores de benefícios.
    """
    # Verifica se há benefícios cadastrados para o contrato
    beneficios = BeneficiosColaborador.objects.filter(contrato=contrato).first()
    if not beneficios:
        return  # Sem benefícios definidos, não há o que recalcular

    # Para cada função vinculada ao contrato, recalcula os valores
    funcoes = CustoDiretoFuncao.objects.filter(contrato=contrato)

    for funcao in funcoes:
        # Recalcula benefícios com base na função e contrato
        from mao_obra.services import BeneficioCustoDiretoService
        funcao.beneficios = BeneficioCustoDiretoService.calcular_beneficios_por_funcao(
            contrato=contrato,
            salario_base_funcao=funcao.salario_base
        )

        funcao.calcular_custo_total()
        funcao.save()


class EquipamentoCustoService:
    """Service para calcular custos de equipamentos por equipe"""
    
    @staticmethod
    def calcular_custos_equipamentos_por_contrato(contrato_id=None, equipe_id=None, regional_id=None, escopo_id=None):
        """
        Calcula custos de equipamentos considerando:
        - Quantidade de equipamentos por equipe
        - Vida útil dos equipamentos 
        - Quantidade de equipes na composição
        """
        try:
            # Busca composições filtradas
            composicoes_queryset = ComposicaoEquipe.objects.select_related(
                'contrato', 'equipe', 'regional', 'escopo'
            ).filter(quantidade_equipes__gt=0)
            
            # Aplica filtros
            if contrato_id:
                composicoes_queryset = composicoes_queryset.filter(contrato__contrato=contrato_id)
            if equipe_id:
                composicoes_queryset = composicoes_queryset.filter(equipe_id=equipe_id)
            if regional_id:
                composicoes_queryset = composicoes_queryset.filter(regional_id=regional_id)
            if escopo_id:
                composicoes_queryset = composicoes_queryset.filter(escopo_id=escopo_id)
            
            custos_por_composicao = []
            totais_por_categoria = {
                'EPI': Decimal('0.00'),
                'EPC': Decimal('0.00'),
                'FERRAMENTAS': Decimal('0.00'),
                'EQUIPAMENTOS_TI': Decimal('0.00'),
                'DESPESAS_TI': Decimal('0.00'),
                'MATERIAIS_CONSUMO': Decimal('0.00'),
                'DESPESAS_DIVERSAS': Decimal('0.00')
            }
            custo_total_geral = Decimal('0.00')
            
            for composicao in composicoes_queryset:
                custos_categorias = EquipamentoCustoService._calcular_custo_por_equipe(
                    composicao.equipe, composicao.contrato
                )
                
                # Multiplica pela quantidade de equipes na composição
                for categoria in custos_categorias:
                    custos_categorias[categoria] *= composicao.quantidade_equipes
                    totais_por_categoria[categoria] += custos_categorias[categoria]
                
                custo_total_composicao = sum(custos_categorias.values())
                custo_total_geral += custo_total_composicao
                
                custos_por_composicao.append({
                    'contrato': composicao.contrato,
                    'composicao': composicao,
                    'equipe': composicao.equipe,
                    'regional': composicao.regional,
                    'escopo': composicao.escopo,
                    'quantidade_equipes': composicao.quantidade_equipes,
                    'custos_categorias': custos_categorias,
                    'custo_total_mensal': custo_total_composicao,
                    'custo_mensal_por_equipe': custo_total_composicao / composicao.quantidade_equipes if composicao.quantidade_equipes > 0 else Decimal('0.00')
                })
            
            return {
                'custos_por_composicao': custos_por_composicao,
                'totais_por_categoria': totais_por_categoria,
                'custo_total_geral': custo_total_geral,
                'tem_dados': len(custos_por_composicao) > 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular custos de equipamentos: {e}")
            return {
                'custos_por_composicao': [],
                'totais_por_categoria': {},
                'custo_total_geral': Decimal('0.00'),
                'tem_dados': False,
                'erro': str(e)
            }
    
    @staticmethod
    def _calcular_custo_por_equipe(equipe, contrato):
        """
        Calcula custo mensal de equipamentos para uma equipe específica.
        
        Lógica: 
        - Para EPI, EPC, Ferramentas, TI: valor_unitário/vida_útil por item, depois somar
        - Para Despesas TI, Materiais, Diversas: somatório direto dos valores mensais
        - Resultado = custo por equipe (antes de multiplicar pela quantidade de equipes)
        """
        custos_por_categoria = {
            'EPI': Decimal('0.00'),
            'EPC': Decimal('0.00'),
            'FERRAMENTAS': Decimal('0.00'),
            'EQUIPAMENTOS_TI': Decimal('0.00'),
            'DESPESAS_TI': Decimal('0.00'),
            'MATERIAIS_CONSUMO': Decimal('0.00'),
            'DESPESAS_DIVERSAS': Decimal('0.00')
        }
        
        # Busca vinculações de equipamentos para esta equipe
        vinculacoes = EquipamentoEquipe.objects.filter(
            equipe=equipe,
            contrato=contrato
        ).select_related(
            'equipamento_vida_util', 
            'equipamento_mensal'
        )
        
        for vinculacao in vinculacoes:
            if vinculacao.equipamento_vida_util:
                # Equipamentos com vida útil (EPI, EPC, Ferramentas, TI)
                equipamento = vinculacao.equipamento_vida_util
                
                # Custo mensal por item = valor_unitário / vida_útil_meses
                custo_mensal_por_item = equipamento.valor_unitario / equipamento.vida_util_meses
                
                # Custo total = custo_mensal_por_item * quantidade_por_equipe
                custo_total_item = custo_mensal_por_item * vinculacao.quantidade_por_equipe
                
                # Soma ao total da categoria
                custos_por_categoria[equipamento.categoria] += custo_total_item
                
            elif vinculacao.equipamento_mensal:
                # Equipamentos mensais (Despesas TI, Materiais, Diversas)
                equipamento = vinculacao.equipamento_mensal
                
                # Custo total = valor_mensal * quantidade_por_equipe
                custo_total_item = equipamento.valor_mensal * vinculacao.quantidade_por_equipe
                
                # Soma ao total da categoria
                custos_por_categoria[equipamento.categoria] += custo_total_item
        
        return custos_por_categoria
    
    @staticmethod
    def get_resumo_equipamentos_por_categoria(contrato_id=None):
        """Retorna resumo de equipamentos cadastrados por categoria"""
        try:
            # Filtrar por contrato se especificado
            filtro_contrato = Q(contrato__contrato=contrato_id) if contrato_id else Q()
            
            # Equipamentos com vida útil
            equipamentos_vida_util = EquipamentoVidaUtil.objects.filter(filtro_contrato)
            
            # Equipamentos mensais  
            equipamentos_mensais = EquipamentoMensal.objects.filter(filtro_contrato)
            
            resumo = {}
            
            # Conta equipamentos com vida útil por categoria
            for categoria, _ in EquipamentoVidaUtil.CATEGORIA_CHOICES:
                count = equipamentos_vida_util.filter(categoria=categoria).count()
                resumo[categoria] = count
            
            # Conta equipamentos mensais por categoria
            for categoria, _ in EquipamentoMensal.CATEGORIA_CHOICES:
                count = equipamentos_mensais.filter(categoria=categoria).count()
                resumo[categoria] = count
            
            return resumo
            
        except Exception as e:
            logger.error(f"Erro ao obter resumo de equipamentos: {e}")
            return {}


def calcular_custos_equipamentos_por_equipe(contrato_id=None, equipe_id=None, regional_id=None, escopo_id=None):
    """Função de conveniência para usar o service"""
    return EquipamentoCustoService.calcular_custos_equipamentos_por_contrato(
        contrato_id=contrato_id,
        equipe_id=equipe_id,
        regional_id=regional_id,
        escopo_id=escopo_id
    )
