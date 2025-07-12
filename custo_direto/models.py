from django.db import models
from decimal import Decimal
from cad_contrato.models import Regional
from cadastro_equipe.models import EscopoAtividade


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

    custo_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

        self.custo_total = (custo_bruto_unitario + self.valor_total_encargos) * self.quantidade_funcionarios * self.composicao.quantidade_equipes
        return self.custo_total

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