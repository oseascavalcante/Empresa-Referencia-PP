from django.db import models
from decimal import Decimal
from cad_contrato.models import CadastroContrato
from cadastro_equipe.models import Equipe


class EquipamentoVidaUtil(models.Model):
    """
    Model para equipamentos com vida útil definida:
    EPI, EPC, Ferramentas, Equipamentos TI
    """
    CATEGORIA_CHOICES = [
        ('EPI', 'EPI - Equipamentos de Proteção Individual'),
        ('EPC', 'EPC - Equipamentos de Proteção Coletiva'),
        ('FERRAMENTAS', 'Ferramentas'),
        ('EQUIPAMENTOS_TI', 'Equipamentos TI'),
    ]
    
    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.CASCADE,
        related_name='equipamentos_vida_util',
        verbose_name='Contrato'
    )
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        verbose_name='Categoria'
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name='Descrição'
    )
    vida_util_meses = models.PositiveIntegerField(
        verbose_name='Vida Útil (meses)'
    )
    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Unitário (R$)'
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantidade'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Equipamento com Vida Útil'
        verbose_name_plural = 'Equipamentos com Vida Útil'
        ordering = ['categoria', 'descricao']
        
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.descricao}"
    
    @property
    def valor_total(self):
        """Calcula o valor total (quantidade * valor unitário)"""
        return self.quantidade * self.valor_unitario
    
    @property
    def custo_mensal(self):
        """Calcula o custo mensal baseado na vida útil"""
        if self.vida_util_meses > 0:
            return self.valor_total / self.vida_util_meses
        return Decimal('0.00')


class EquipamentoMensal(models.Model):
    """
    Model para equipamentos/despesas com custo mensal:
    Despesas TI, Materiais Consumo, Despesas Diversas
    """
    CATEGORIA_CHOICES = [
        ('DESPESAS_TI', 'Despesas TI'),
        ('MATERIAIS_CONSUMO', 'Materiais de Consumo'),
        ('DESPESAS_DIVERSAS', 'Despesas Diversas'),
    ]
    
    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.CASCADE,
        related_name='equipamentos_mensais',
        verbose_name='Contrato'
    )
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        verbose_name='Categoria'
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name='Descrição'
    )
    valor_mensal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Mensal (R$)'
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantidade'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Equipamento/Despesa Mensal'
        verbose_name_plural = 'Equipamentos/Despesas Mensais'
        ordering = ['categoria', 'descricao']
        
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.descricao}"
    
    @property
    def custo_total_mensal(self):
        """Calcula o custo total mensal (quantidade * valor mensal)"""
        return self.quantidade * self.valor_mensal


class EquipamentoEquipe(models.Model):
    """
    Model para vincular equipamentos às equipes com quantidades específicas
    """
    # Relacionamentos com equipamentos (apenas um será preenchido)
    equipamento_vida_util = models.ForeignKey(
        EquipamentoVidaUtil,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vinculacoes_equipe'
    )
    equipamento_mensal = models.ForeignKey(
        EquipamentoMensal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='vinculacoes_equipe'
    )
    
    # Vinculação com contrato
    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.CASCADE,
        related_name='equipamentos_equipe',
        verbose_name='Contrato',
        null=True,
        blank=True
    )
    
    # Vinculação com equipe
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.CASCADE,
        related_name='equipamentos_vinculados',
        verbose_name='Equipe'
    )
    
    # Quantidade específica para esta equipe
    quantidade_por_equipe = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantidade por Equipe'
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Equipamento por Equipe'
        verbose_name_plural = 'Equipamentos por Equipe'
        
        # Garante que não há duplicação de vinculação
        constraints = [
            models.UniqueConstraint(
                fields=['equipamento_vida_util', 'equipe'],
                name='unique_vida_util_equipe',
                condition=models.Q(equipamento_vida_util__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['equipamento_mensal', 'equipe'],
                name='unique_mensal_equipe',
                condition=models.Q(equipamento_mensal__isnull=False)
            ),
        ]
        
        # Valida que apenas um tipo de equipamento está vinculado
        constraints.append(
            models.CheckConstraint(
                check=(
                    models.Q(equipamento_vida_util__isnull=False, equipamento_mensal__isnull=True) |
                    models.Q(equipamento_vida_util__isnull=True, equipamento_mensal__isnull=False)
                ),
                name='equipamento_equipe_only_one_type'
            )
        )
    
    def __str__(self):
        if self.equipamento_vida_util:
            return f"{self.equipe.nome} - {self.equipamento_vida_util.descricao}"
        elif self.equipamento_mensal:
            return f"{self.equipe.nome} - {self.equipamento_mensal.descricao}"
        return f"{self.equipe.nome} - Equipamento"
    
    @property
    def equipamento(self):
        """Retorna o equipamento vinculado (independente do tipo)"""
        return self.equipamento_vida_util or self.equipamento_mensal
    
    @property
    def custo_total_equipe(self):
        """Calcula o custo total para esta equipe"""
        if self.equipamento_vida_util:
            return self.equipamento_vida_util.custo_mensal * self.quantidade_por_equipe
        elif self.equipamento_mensal:
            return self.equipamento_mensal.valor_mensal * self.quantidade_por_equipe
        return Decimal('0.00')
