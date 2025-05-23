from django.db import models
from decimal import Decimal

class CustoDiretoFuncao(models.Model):
    contrato = models.ForeignKey('cad_contrato.CadastroContrato', on_delete=models.CASCADE, related_name='custos_diretos_funcoes')
    composicao = models.ForeignKey('cadastro_equipe.ComposicaoEquipe', on_delete=models.CASCADE, related_name='custos_diretos')
    funcao = models.ForeignKey('cadastro_equipe.Funcao', on_delete=models.PROTECT, related_name='custos_diretos')


    quantidade_funcionarios = models.PositiveIntegerField(default=1)

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

    custo_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

        custo_bruto_total = custo_bruto_unitario * self.quantidade_funcionarios

        self.valor_grupo_a = custo_bruto_total * (self.percentual_grupo_a / Decimal('100'))
        self.valor_grupo_b = custo_bruto_total * (self.percentual_grupo_b / Decimal('100'))
        self.valor_grupo_c = custo_bruto_total * (self.percentual_grupo_c / Decimal('100'))
        self.valor_grupo_d = custo_bruto_total * (self.percentual_grupo_d / Decimal('100'))

        self.valor_total_encargos = custo_bruto_total * (self.percentual_grupo_e / Decimal('100'))

        self.custo_total = custo_bruto_total + self.valor_total_encargos
        return self.custo_total

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contrato', 'composicao', 'funcao'], name='unique_custo_por_funcao')
        ]

    def __str__(self):
        return f"{self.contrato} - {self.composicao.equipe.nome} - {self.funcao.nome}"    
    


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