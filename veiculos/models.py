from django.db import models
from decimal import Decimal
from cad_contrato.models import CadastroContrato, Regional
from cadastro_equipe.models import EscopoAtividade

class TipoVeiculo(models.Model):
    """
    Master data para tipos de veículos, implementos e equipamentos.
    Não parametrizado por contrato - dados globais do sistema.
    """
    CATEGORIA_CHOICES = [
        ('veiculo_leve', 'Veículo Leve'),
        ('veiculo_pesado', 'Veículo Pesado'),
        ('implemento', 'Implemento'),
        ('equipamento', 'Equipamento'),
    ]
    
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Tipo")
    categoria = models.CharField(
        max_length=50, 
        choices=CATEGORIA_CHOICES,
        verbose_name="Categoria"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    especificacoes_tecnicas = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Especificações Técnicas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Veículo"
        verbose_name_plural = "Tipos de Veículos"
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class PrecoCombustivel(models.Model):
    """
    Configuração de preços de combustível por contrato.
    Permite diferentes preços para cada tipo de combustível.
    """
    TIPO_COMBUSTIVEL_CHOICES = [
        ('gasolina', 'Gasolina'),
        ('etanol', 'Etanol'),
        ('diesel', 'Diesel'),
        ('flex', 'Flex (Gasolina/Etanol)'),
        ('gnv', 'GNV'),
        ('eletrico', 'Elétrico'),
    ]

    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.PROTECT,
        related_name="precos_combustivel",
        verbose_name="Contrato"
    )
    tipo_combustivel = models.CharField(
        max_length=20,
        choices=TIPO_COMBUSTIVEL_CHOICES,
        verbose_name="Tipo de Combustível"
    )
    preco_por_litro = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        verbose_name="Preço por Litro (R$)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preço de Combustível"
        verbose_name_plural = "Preços de Combustível"
        unique_together = ('contrato', 'tipo_combustivel')
        ordering = ['contrato', 'tipo_combustivel']

    def __str__(self):
        return f"{self.get_tipo_combustivel_display()}: R$ {self.preco_por_litro} ({self.contrato})"


class Veiculo(models.Model):
    """
    Cadastro de veículos parametrizado por contrato.
    Controla tipos de veículos sem identificação individual.
    """
    TIPO_COMBUSTIVEL_CHOICES = [
        ('gasolina', 'Gasolina'),
        ('etanol', 'Etanol'),
        ('diesel', 'Diesel'),
        ('flex', 'Flex (Gasolina/Etanol)'),
        ('gnv', 'GNV'),
        ('eletrico', 'Elétrico'),
    ]

    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.PROTECT,
        related_name="veiculos",
        verbose_name="Contrato"
    )
    tipo_veiculo = models.ForeignKey(
        TipoVeiculo,
        on_delete=models.PROTECT,
        related_name="veiculos",
        verbose_name="Tipo de Veículo"
    )

    # Dados financeiros
    valor_aquisicao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor de Aquisição (R$)"
    )
    valor_locacao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor de Locação Mensal (R$)"
    )
    vida_util_meses = models.PositiveIntegerField(
        default=60,
        verbose_name="Vida Útil (meses)"
    )
    custo_mensal_seguro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Custo Mensal de Seguro (R$)"
    )
    custo_mensal_manutencao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name="Custo Mensal de Manutenção (R$)"
    )

    # Dados de combustível
    tipo_combustivel = models.CharField(
        max_length=20,
        choices=TIPO_COMBUSTIVEL_CHOICES,
        verbose_name="Tipo de Combustível"
    )
    eficiencia_km_litro = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Eficiência (Km/L)"
    )

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Veículo"
        verbose_name_plural = "Veículos"
        unique_together = ('contrato', 'tipo_veiculo')
        ordering = ['contrato', 'tipo_veiculo__categoria', 'tipo_veiculo__nome']

    def __str__(self):
        return f"{self.tipo_veiculo.nome} - {self.contrato}"

    @property
    def custo_mensal_combustivel(self):
        """
        Custo mensal de combustível será calculado em outra model.
        Por enquanto retorna 0.
        """
        return Decimal('0.00')

    @property
    def custo_depreciacao_mensal(self):
        """
        Calcula depreciação mensal linear
        (sem valor residual conforme especificação).
        """
        if self.vida_util_meses > 0:
            return self.valor_aquisicao / self.vida_util_meses
        return Decimal('0.00')

    @property
    def custo_total_mensal(self):
        """
        Custo total mensal do veículo incluindo:
        - Depreciação
        - Seguro
        - Manutenção
        - Combustível (calculado automaticamente)
        """
        return (
            self.custo_depreciacao_mensal +
            self.custo_mensal_seguro +
            self.custo_mensal_manutencao +
            self.custo_mensal_combustivel
        )


class AtribuicaoVeiculo(models.Model):
    """
    Atribuição de veículos por quantidade a regionais e escopos.
    Sem datas - controle apenas por quantidade.
    """
    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.PROTECT,
        related_name="atribuicoes_veiculo",
        verbose_name="Contrato"
    )
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name="atribuicoes",
        verbose_name="Veículo"
    )
    regional = models.ForeignKey(
        Regional,
        on_delete=models.PROTECT,
        related_name="atribuicoes_veiculo",
        verbose_name="Regional"
    )
    escopo = models.ForeignKey(
        EscopoAtividade,
        on_delete=models.PROTECT,
        related_name="atribuicoes_veiculo",
        verbose_name="Escopo de Atividade"
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00,
        verbose_name="Quantidade"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Atribuição de Veículo"
        verbose_name_plural = "Atribuições de Veículos"
        unique_together = ('contrato', 'veiculo', 'regional', 'escopo')
        ordering = ['contrato', 'regional', 'escopo', 'veiculo']

    def __str__(self):
        return f"{self.veiculo} - {self.regional} - {self.escopo} (Qtd: {self.quantidade})"

    @property
    def custo_total_mensal_atribuicao(self):
        """
        Custo total mensal desta atribuição específica
        (custo unitário do veículo * quantidade).
        """
        return self.veiculo.custo_total_mensal * self.quantidade
