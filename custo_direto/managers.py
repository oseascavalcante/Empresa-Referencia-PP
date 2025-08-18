from django.db import models
from django.db.models import Sum, Avg, Count, Q, F, Case, When, DecimalField, Value
from decimal import Decimal


class CustoDiretoFuncaoQuerySet(models.QuerySet):
    """QuerySet customizado para CustoDiretoFuncao com otimizações."""
    
    def otimizado(self):
        """QuerySet com select_related e prefetch_related otimizados."""
        return self.select_related(
            'contrato',
            'regional', 
            'escopo',
            'composicao__equipe',
            'composicao__veiculo__tipo_veiculo',
            'funcao'
        ).prefetch_related(
            'composicao__funcoes',
            'composicao__equipamentos_vinculados__equipamento_vida_util',
            'composicao__equipamentos_vinculados__equipamento_mensal'
        )
    
    def por_contrato(self, contrato_id):
        """Filtra por contrato específico."""
        return self.filter(contrato__contrato=contrato_id)
    
    def por_regional(self, regional_id):
        """Filtra por regional específica."""
        return self.filter(regional_id=regional_id)
    
    def por_escopo(self, escopo_id):
        """Filtra por escopo específico.""" 
        return self.filter(escopo_id=escopo_id)
    
    def com_funcionarios(self):
        """Filtra apenas registros com funcionários."""
        return self.filter(quantidade_funcionarios__gt=0)
    
    def com_custos(self):
        """Filtra apenas registros com custos calculados."""
        return self.filter(custo_total__gt=0)


class CustoDiretoFuncaoManager(models.Manager):
    """Manager customizado para CustoDiretoFuncao com métodos de agregação."""
    
    def get_queryset(self):
        return CustoDiretoFuncaoQuerySet(self.model, using=self._db)
    
    def otimizado(self):
        return self.get_queryset().otimizado()
    
    def por_contrato(self, contrato_id):
        return self.get_queryset().por_contrato(contrato_id)
    
    def por_regional(self, regional_id):
        return self.get_queryset().por_regional(regional_id)
    
    def por_escopo(self, escopo_id):
        return self.get_queryset().por_escopo(escopo_id)
    
    def com_funcionarios(self):
        return self.get_queryset().com_funcionarios()
    
    def com_custos(self):
        return self.get_queryset().com_custos()
    
    def consolidacao_por_contrato(self, contrato_id):
        """
        Retorna dados consolidados por contrato.
        """
        return self.otimizado().por_contrato(contrato_id).com_custos().aggregate(
            total_mao_obra=Sum('custo_total'),
            total_funcionarios=Sum('quantidade_total_funcionarios'),
            total_funcoes=Count('id'),
            custo_medio_funcionario=Case(
                When(quantidade_total_funcionarios__gt=0,
                     then=F('custo_total') / F('quantidade_total_funcionarios')),
                default=Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            total_beneficios=Sum('beneficios'),
            total_encargos=Sum('valor_total_encargos')
        )
    
    def consolidacao_por_regional(self, contrato_id):
        """
        Retorna dados consolidados por regional dentro de um contrato.
        """
        return self.otimizado().por_contrato(contrato_id).com_custos().values(
            'regional__id',
            'regional__nome'
        ).annotate(
            total_mao_obra=Sum('custo_total'),
            total_funcionarios=Sum('quantidade_total_funcionarios'),
            total_funcoes=Count('id'),
            custo_medio_funcionario=Case(
                When(total_funcionarios__gt=0,
                     then=F('total_mao_obra') / F('total_funcionarios')),
                default=Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).order_by('regional__nome')
    
    def consolidacao_por_escopo(self, contrato_id):
        """
        Retorna dados consolidados por escopo dentro de um contrato.
        """
        return self.otimizado().por_contrato(contrato_id).com_custos().values(
            'escopo__id',
            'escopo__nome'
        ).annotate(
            total_mao_obra=Sum('custo_total'),
            total_funcionarios=Sum('quantidade_total_funcionarios'),
            total_funcoes=Count('id'),
            custo_medio_funcionario=Case(
                When(total_funcionarios__gt=0,
                     then=F('total_mao_obra') / F('total_funcionarios')),
                default=Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).order_by('escopo__nome')
    
    def consolidacao_por_equipe(self, contrato_id):
        """
        Retorna dados consolidados por equipe dentro de um contrato.
        """
        return self.otimizado().por_contrato(contrato_id).com_custos().values(
            'composicao__equipe__id',
            'composicao__equipe__nome'
        ).annotate(
            total_mao_obra=Sum('custo_total'),
            total_funcionarios=Sum('quantidade_total_funcionarios'),
            total_funcoes=Count('id'),
            quantidade_equipes=F('composicao__quantidade_equipes'),
            custo_por_equipe=Case(
                When(composicao__quantidade_equipes__gt=0,
                     then=F('total_mao_obra') / F('composicao__quantidade_equipes')),
                default=Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).order_by('composicao__equipe__nome')
    
    def top_custos_por_funcao(self, contrato_id, limit=10):
        """
        Retorna as top N funções com maior custo em um contrato.
        """
        return self.otimizado().por_contrato(contrato_id).com_custos().values(
            'funcao__nome',
            'funcao__salario'
        ).annotate(
            total_custo=Sum('custo_total'),
            total_funcionarios=Sum('quantidade_total_funcionarios')
        ).order_by('-total_custo')[:limit]
    
    def resumo_encargos_sociais(self, contrato_id):
        """
        Retorna resumo dos encargos sociais por grupo.
        """
        return self.otimizado().por_contrato(contrato_id).com_custos().aggregate(
            total_grupo_a=Sum(
                F('valor_grupo_a') * F('quantidade_total_funcionarios')
            ),
            total_grupo_b=Sum(
                F('valor_grupo_b') * F('quantidade_total_funcionarios')
            ),
            total_grupo_c=Sum(
                F('valor_grupo_c') * F('quantidade_total_funcionarios')
            ),
            total_encargos=Sum('valor_total_encargos'),
            percentual_medio_grupo_a=Avg('percentual_grupo_a'),
            percentual_medio_grupo_b=Avg('percentual_grupo_b'),
            percentual_medio_grupo_c=Avg('percentual_grupo_c')
        )


class ConsolidacaoQuerySet(models.QuerySet):
    """QuerySet para models de consolidação."""
    
    def atualizados_recentemente(self, dias=7):
        """Filtra consolidações atualizadas nos últimos N dias."""
        from django.utils import timezone
        from datetime import timedelta
        
        data_limite = timezone.now() - timedelta(days=dias)
        return self.filter(updated_at__gte=data_limite)
    
    def por_periodo(self, data_inicio, data_fim):
        """Filtra consolidações por período."""
        return self.filter(
            data_consolidacao__range=[data_inicio, data_fim]
        )


class ConsolidacaoManager(models.Manager):
    """Manager base para models de consolidação."""
    
    def get_queryset(self):
        return ConsolidacaoQuerySet(self.model, using=self._db)
    
    def atualizados_recentemente(self, dias=7):
        return self.get_queryset().atualizados_recentemente(dias)
    
    def por_periodo(self, data_inicio, data_fim):
        return self.get_queryset().por_periodo(data_inicio, data_fim)
    
    def necessitam_atualizacao(self):
        """
        Retorna registros que precisam ser atualizados
        baseado em mudanças nos dados fonte.
        """
        # Implementação específica baseada em timestamps
        # ou flags de invalidação
        pass