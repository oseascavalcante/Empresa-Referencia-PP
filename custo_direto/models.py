from django.db import models
from decimal import Decimal
from cad_contrato.models import Regional
from cadastro_equipe.models import EscopoAtividade
from .managers import CustoDiretoFuncaoManager, ConsolidacaoManager


class CustoDiretoFuncao(models.Model):
    contrato = models.ForeignKey(
        'cad_contrato.CadastroContrato',
        on_delete=models.CASCADE,
        related_name='custos_diretos_funcoes'
    )
    regional = models.ForeignKey(Regional, on_delete=models.CASCADE, null=True, blank=True)
    escopo = models.ForeignKey(EscopoAtividade, on_delete=models.CASCADE, null=True, blank=True)
    composicao = models.ForeignKey(
        'cadastro_equipe.ComposicaoEquipe',
        on_delete=models.CASCADE,
        related_name='custos_diretos'
    )
    funcao = models.ForeignKey(
        'cadastro_equipe.Funcao',
        on_delete=models.PROTECT,
        related_name='custos_diretos'
    )

    quantidade_funcionarios = models.PositiveIntegerField(default=1)
    quantidade_total_funcionarios = models.PositiveIntegerField(default=0)  # ✅ Novo campo persistente

    salario_base = models.DecimalField(max_digits=12, decimal_places=2)
    adicional_periculosidade = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_horas_extras_50 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_horas_extras_100 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_adicional_noturno = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_prontidao = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_sobreaviso = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outros_custos = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    beneficios = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    percentual_grupo_a = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_grupo_b = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_grupo_c = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_grupo_d = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentual_grupo_e = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    valor_grupo_a = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_grupo_b = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_grupo_c = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_grupo_d = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_total_encargos = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Custos de veículos
    custo_veiculos = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo de Veículos")
    km_rodado_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="KM Rodados Total")
    custo_combustivel = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Custo de Combustível")
    
    # Custos de equipamentos por categoria
    custo_epi = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo EPI")
    custo_epc = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo EPC")
    custo_ferramentas = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Ferramentas")
    custo_equipamentos_ti = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Equipamentos TI")
    custo_despesas_ti = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Despesas TI")
    custo_materiais_consumo = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Materiais de Consumo")
    custo_despesas_diversas = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Despesas Diversas")

    custo_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager customizado
    objects = CustoDiretoFuncaoManager()

    def calcular_quantidade_total_funcionarios(self):
        """
        Calcula a quantidade total de funcionários considerando a quantidade de equipes.
        """
        quantidade_equipes = self.composicao.quantidade_equipes or 0
        return int(self.quantidade_funcionarios * quantidade_equipes)

    def calcular_custo_total(self):
        """
        Calcula o custo total consolidado da função no contrato,
        considerando salários, adicionais, benefícios e encargos sociais.
        """
        custo_bruto_unitario = (
            self.salario_base +
            self.adicional_periculosidade +
            self.valor_horas_extras_50 +
            self.valor_horas_extras_100 +
            self.valor_adicional_noturno +
            self.valor_prontidao +
            self.valor_sobreaviso +
            self.outros_custos +
            self.beneficios
        )
        
        #Custo para aplicar encargos sociais grupos A, B e C
        custo_funcionario_horas_normais = (
            self.salario_base +
            self.adicional_periculosidade +
            self.outros_custos 
        )
        # Custo para aplicar encargos sociais grupos A e B
        custo_funcionario_horas_extras = (
            self.valor_horas_extras_50 +
            self.valor_horas_extras_100 +
            self.valor_adicional_noturno +
            self.valor_prontidao +
            self.valor_sobreaviso 
        )

        # ✅ Conversão explícita dos percentuais para Decimal
        grupo_a = Decimal(str(self.percentual_grupo_a or 0))
        grupo_b = Decimal(str(self.percentual_grupo_b or 0))
        grupo_c = Decimal(str(self.percentual_grupo_c or 0))
        grupo_d = Decimal(str(self.percentual_grupo_d or 0))
        grupo_e = Decimal(str(self.percentual_grupo_e or 0))

        valor_encargos_he =  custo_funcionario_horas_extras * ((grupo_a + grupo_b) / Decimal('100'))  # Encargos sociais para horas extras (grupos A e B)           
        valor_encargos_hn =  custo_funcionario_horas_normais * (grupo_e / Decimal('100')) # Encargos sociais para horas normais (grupo E) 
           
        self.valor_total_encargos = valor_encargos_he + valor_encargos_hn # Valor total dos encargos sociais por funcionário

        # Calcular custos de mão de obra
        custo_mao_obra = (custo_bruto_unitario + self.valor_total_encargos) * self.quantidade_funcionarios * self.composicao.quantidade_equipes
        
        # Calcular custos de veículos
        self.calcular_custos_veiculos()
        
        # Calcular custos de equipamentos
        self.calcular_custos_equipamentos()
        
        # Custo total consolidado
        self.custo_total = (
            custo_mao_obra + 
            self.custo_veiculos + 
            self.custo_combustivel +
            self.custo_epi + 
            self.custo_epc + 
            self.custo_ferramentas + 
            self.custo_equipamentos_ti + 
            self.custo_despesas_ti + 
            self.custo_materiais_consumo + 
            self.custo_despesas_diversas
        )
        
        return self.custo_total

    def calcular_custos_veiculos(self):
        """
        Calcula custos de veículos para esta composição.
        """
        if not self.composicao.veiculo or not self.composicao.quantidade_veiculos:
            self.custo_veiculos = Decimal('0.00')
            self.km_rodado_total = Decimal('0.00') 
            self.custo_combustivel = Decimal('0.00')
            return

        # Custo base do veículo (locação ou próprio)
        valor_unitario_veiculo = self.composicao.valor_veiculo
        quantidade_total_veiculos = self.composicao.quantidade_veiculos * self.composicao.quantidade_equipes
        
        self.custo_veiculos = valor_unitario_veiculo * quantidade_total_veiculos
        self.km_rodado_total = self.composicao.km_rodado * self.composicao.quantidade_equipes
        
        # Calcular custo de combustível baseado em KM e eficiência
        if self.composicao.veiculo and self.km_rodado_total > 0:
            try:
                veiculo = self.composicao.veiculo
                litros_necessarios = self.km_rodado_total / veiculo.eficiencia_km_litro
                
                # Buscar preço do combustível para o contrato
                from veiculos.models import PrecoCombustivel
                preco_combustivel = PrecoCombustivel.objects.filter(
                    contrato=self.contrato,
                    tipo_combustivel=veiculo.tipo_combustivel
                ).first()
                
                if preco_combustivel:
                    self.custo_combustivel = litros_necessarios * preco_combustivel.preco_por_litro * quantidade_total_veiculos
                else:
                    self.custo_combustivel = Decimal('0.00')
                    
            except (AttributeError, ZeroDivisionError):
                self.custo_combustivel = Decimal('0.00')
        else:
            self.custo_combustivel = Decimal('0.00')
    
    def calcular_custos_equipamentos(self):
        """
        Calcula custos de equipamentos para esta composição.
        """
        # Resetar custos
        self.custo_epi = Decimal('0.00')
        self.custo_epc = Decimal('0.00')
        self.custo_ferramentas = Decimal('0.00')
        self.custo_equipamentos_ti = Decimal('0.00')
        self.custo_despesas_ti = Decimal('0.00')
        self.custo_materiais_consumo = Decimal('0.00')
        self.custo_despesas_diversas = Decimal('0.00')
        
        # Buscar equipamentos vinculados à equipe da composição
        from equipamentos.models import EquipamentoEquipe
        
        equipamentos_vinculados = EquipamentoEquipe.objects.filter(
            equipe=self.composicao.equipe,
            contrato=self.contrato
        ).select_related('equipamento_vida_util', 'equipamento_mensal')
        
        quantidade_equipes = self.composicao.quantidade_equipes
        
        for vinculacao in equipamentos_vinculados:
            if vinculacao.equipamento_vida_util:
                # Equipamentos com vida útil
                equipamento = vinculacao.equipamento_vida_util
                custo_mensal_por_equipe = equipamento.custo_mensal * vinculacao.quantidade_por_equipe
                custo_total = custo_mensal_por_equipe * quantidade_equipes
                
                # Distribuir por categoria
                if equipamento.categoria == 'EPI':
                    self.custo_epi += custo_total
                elif equipamento.categoria == 'EPC':
                    self.custo_epc += custo_total
                elif equipamento.categoria == 'FERRAMENTAS':
                    self.custo_ferramentas += custo_total
                elif equipamento.categoria == 'EQUIPAMENTOS_TI':
                    self.custo_equipamentos_ti += custo_total
                    
            elif vinculacao.equipamento_mensal:
                # Equipamentos mensais
                equipamento = vinculacao.equipamento_mensal
                custo_mensal_por_equipe = equipamento.valor_mensal * vinculacao.quantidade_por_equipe
                custo_total = custo_mensal_por_equipe * quantidade_equipes
                
                # Distribuir por categoria
                if equipamento.categoria == 'DESPESAS_TI':
                    self.custo_despesas_ti += custo_total
                elif equipamento.categoria == 'MATERIAIS_CONSUMO':
                    self.custo_materiais_consumo += custo_total
                elif equipamento.categoria == 'DESPESAS_DIVERSAS':
                    self.custo_despesas_diversas += custo_total

    def calcular_beneficios(self):
        from mao_obra.services import BeneficioCustoDiretoService  # Agora é um arquivo, não uma pasta
        return BeneficioCustoDiretoService.calcular_beneficios_por_funcao(
            contrato=self.contrato,
            salario_base_funcao=self.salario_base
        )

  
    def save(self, *args, **kwargs):
        self.quantidade_total_funcionarios = self.calcular_quantidade_total_funcionarios()
        self.beneficios = self.calcular_beneficios()
        self.calcular_custo_total()
        super().save(*args, **kwargs)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contrato', 'composicao', 'funcao'], name='unique_custo_por_funcao')
        ]

    def __str__(self):
        return f"{self.contrato} - {self.composicao.equipe.nome} - {self.funcao.nome}"   

class ConsolidacaoCustoContrato(models.Model):
    """
    Consolidação de todos os custos por contrato.
    """
    contrato = models.OneToOneField(
        'cad_contrato.CadastroContrato', 
        on_delete=models.CASCADE, 
        related_name='consolidacao_custos'
    )
    
    # Custos por categoria
    custo_mao_obra = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Mão de Obra")
    custo_veiculos = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Veículos")
    custo_combustivel = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Combustível")
    custo_equipamentos = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Equipamentos")
    custo_total = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Total")
    
    # Detalhamento de equipamentos
    custo_epi = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo EPI")
    custo_epc = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo EPC")
    custo_ferramentas = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Ferramentas")
    custo_equipamentos_ti = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Equipamentos TI")
    custo_despesas_ti = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Despesas TI")
    custo_materiais_consumo = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Materiais de Consumo")
    custo_despesas_diversas = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Custo Despesas Diversas")
    
    # Totais gerais
    total_funcionarios = models.PositiveIntegerField(default=0, verbose_name="Total de Funcionários")
    total_equipes = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total de Equipes")
    total_veiculos = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total de Veículos")
    
    # Metadados
    data_consolidacao = models.DateTimeField(auto_now=True, verbose_name="Data da Consolidação")
    versao_calculo = models.CharField(max_length=10, default="1.0", verbose_name="Versão do Cálculo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager customizado
    objects = ConsolidacaoManager()
    
    class Meta:
        verbose_name = "Consolidação de Custos por Contrato"
        verbose_name_plural = "Consolidações de Custos por Contrato"
        ordering = ['-data_consolidacao']
    
    def __str__(self):
        return f"Consolidação - {self.contrato.contrato} ({self.data_consolidacao.strftime('%d/%m/%Y %H:%M')})"
    
    def consolidar(self):
        """
        Executa a consolidação de todos os custos do contrato.
        """
        custos_funcoes = CustoDiretoFuncao.objects.filter(contrato=self.contrato).aggregate(
            total_mao_obra=models.Sum('custo_total') or Decimal('0.00'),
            total_veiculos=models.Sum('custo_veiculos') or Decimal('0.00'),
            total_combustivel=models.Sum('custo_combustivel') or Decimal('0.00'),
            total_epi=models.Sum('custo_epi') or Decimal('0.00'),
            total_epc=models.Sum('custo_epc') or Decimal('0.00'),
            total_ferramentas=models.Sum('custo_ferramentas') or Decimal('0.00'),
            total_equipamentos_ti=models.Sum('custo_equipamentos_ti') or Decimal('0.00'),
            total_despesas_ti=models.Sum('custo_despesas_ti') or Decimal('0.00'),
            total_materiais_consumo=models.Sum('custo_materiais_consumo') or Decimal('0.00'),
            total_despesas_diversas=models.Sum('custo_despesas_diversas') or Decimal('0.00'),
            total_funcionarios=models.Sum('quantidade_total_funcionarios') or 0
        )
        
        # Atualizar campos
        self.custo_mao_obra = custos_funcoes['total_mao_obra']
        self.custo_veiculos = custos_funcoes['total_veiculos']
        self.custo_combustivel = custos_funcoes['total_combustivel']
        self.custo_epi = custos_funcoes['total_epi']
        self.custo_epc = custos_funcoes['total_epc']
        self.custo_ferramentas = custos_funcoes['total_ferramentas']
        self.custo_equipamentos_ti = custos_funcoes['total_equipamentos_ti']
        self.custo_despesas_ti = custos_funcoes['total_despesas_ti']
        self.custo_materiais_consumo = custos_funcoes['total_materiais_consumo']
        self.custo_despesas_diversas = custos_funcoes['total_despesas_diversas']
        
        # Totais calculados
        self.custo_equipamentos = (
            self.custo_epi + self.custo_epc + self.custo_ferramentas +
            self.custo_equipamentos_ti + self.custo_despesas_ti + 
            self.custo_materiais_consumo + self.custo_despesas_diversas
        )
        
        self.custo_total = (
            self.custo_mao_obra + self.custo_veiculos + 
            self.custo_combustivel + self.custo_equipamentos
        )
        
        self.total_funcionarios = custos_funcoes['total_funcionarios']
        
        # Consolidar totais de equipes e veículos
        from cadastro_equipe.models import ComposicaoEquipe
        composicoes = ComposicaoEquipe.objects.filter(contrato=self.contrato).aggregate(
            total_equipes=models.Sum('quantidade_equipes') or Decimal('0.00'),
            total_veiculos=models.Sum('quantidade_veiculos') or Decimal('0.00')
        )
        
        self.total_equipes = composicoes['total_equipes']
        self.total_veiculos = composicoes['total_veiculos']


class ConsolidacaoCustoRegional(models.Model):
    """
    Consolidação de custos por regional dentro de um contrato.
    """
    contrato = models.ForeignKey(
        'cad_contrato.CadastroContrato',
        on_delete=models.CASCADE,
        related_name='consolidacoes_regionais'
    )
    regional = models.ForeignKey(
        Regional,
        on_delete=models.CASCADE,
        related_name='consolidacoes_custos'
    )
    
    # Custos por categoria (mesma estrutura do contrato)
    custo_mao_obra = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_veiculos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_combustivel = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_equipamentos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Totais
    total_funcionarios = models.PositiveIntegerField(default=0)
    total_equipes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    data_consolidacao = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager customizado
    objects = ConsolidacaoManager()
    
    class Meta:
        verbose_name = "Consolidação de Custos por Regional"
        verbose_name_plural = "Consolidações de Custos por Regional"
        unique_together = ('contrato', 'regional')
        ordering = ['contrato', 'regional__nome']


class ConsolidacaoCustoPeriodo(models.Model):
    """
    Consolidação de custos por período (mensal/anual) para análises temporais.
    """
    TIPO_PERIODO_CHOICES = [
        ('MENSAL', 'Mensal'),
        ('TRIMESTRAL', 'Trimestral'),
        ('ANUAL', 'Anual'),
    ]
    
    contrato = models.ForeignKey(
        'cad_contrato.CadastroContrato',
        on_delete=models.CASCADE,
        related_name='consolidacoes_periodo'
    )
    
    tipo_periodo = models.CharField(max_length=20, choices=TIPO_PERIODO_CHOICES)
    ano = models.PositiveIntegerField()
    mes = models.PositiveIntegerField(null=True, blank=True)  # Para períodos mensais
    trimestre = models.PositiveIntegerField(null=True, blank=True)  # Para períodos trimestrais
    
    # Custos (mesma estrutura)
    custo_mao_obra = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_veiculos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_combustivel = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_equipamentos = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    custo_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    data_consolidacao = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager customizado
    objects = ConsolidacaoManager()
    
    class Meta:
        verbose_name = "Consolidação de Custos por Período"
        verbose_name_plural = "Consolidações de Custos por Período"
        unique_together = ('contrato', 'tipo_periodo', 'ano', 'mes', 'trimestre')
        ordering = ['-ano', '-mes', '-trimestre']


# Manter modelo antigo para compatibilidade
class CustoDireto(models.Model):
    contrato = models.OneToOneField('cad_contrato.CadastroContrato', on_delete=models.CASCADE, related_name='custo_direto')
    custo_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calcular_custo_total(self):
        """
        Soma o custo total de todas as funções associadas ao contrato.
        """
        total_funcoes = sum(funcao.custo_total for funcao in self.contrato.custos_diretos_funcoes.all())
        self.custo_total = total_funcoes
        return self.custo_total

    def __str__(self):
        return f"Custo Direto do Contrato {self.contrato}"