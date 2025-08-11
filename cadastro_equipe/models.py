from django.db import models
from cad_contrato.models import CadastroContrato, Regional  # Importando a model do outro app
import uuid
"""
Modelos para gerenciar equipes, funções e suas composições em uma aplicação Django.
Classes:
    Equipe:
        Representa uma equipe com um nome único.
    Funcao:
        Representa uma função ou cargo dentro de uma equipe, incluindo seu nome e salário.
    ComposicaoEquipe:
        Representa a composição de uma equipe para um contrato específico, incluindo detalhes como
        quantidade de equipes, datas de mobilização e desmobilização, e observações adicionais.
    FuncaoEquipe:
        Representa as funções dentro de uma composição de equipe, incluindo a quantidade de funcionários,
        custos adicionais e condições de trabalho, como horas extras e turnos noturnos.
"""
class EscopoAtividade(models.Model):
    contrato = models.ForeignKey(
        CadastroContrato,
        on_delete=models.PROTECT,
        related_name="escopos",
        verbose_name="Contrato",
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Escopo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Escopo")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["contrato", "nome"],
                name="uniq_escopo_por_contrato",
            )
        ]

    def __str__(self):
        return self.nome

class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    contrato = models.ForeignKey(
        'cad_contrato.CadastroContrato',
        on_delete=models.PROTECT,
        related_name='equipes'
    )
    descricao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição breve")  # NOVO

    class Meta:
        unique_together = ('contrato', 'nome')

    def __str__(self):
        return self.nome


class Funcao(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.PROTECT, related_name="funcoes")
    nome = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('contrato', 'nome')

    def __str__(self):
        return f"{self.nome} - R$ {self.salario} ({self.contrato})"

#Cadastro das equipes
class ComposicaoEquipe(models.Model):
    composicao_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.PROTECT)
    regional = models.ForeignKey(Regional, on_delete=models.PROTECT, related_name="composicoes", verbose_name="Regional")
    escopo = models.ForeignKey(EscopoAtividade, on_delete=models.PROTECT, related_name="composicoes", verbose_name="Escopo da Atividade")
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT)
    quantidade_equipes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_mobilizacao = models.DateField(default='2025-01-01')
    data_desmobilizacao = models.DateField(default='2028-01-01')
    prefixo_equipe = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)  # Agora salva uma única vez por composição
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['contrato', 'regional', 'escopo', 'equipe'],
                name='unique_composicao_por_regional_escopo_equipe'
            )
        ]
        verbose_name = "Composição de Equipe"
        verbose_name_plural = "Composições de Equipe"

#Cadastro das funções dentro da Equipe
class FuncaoEquipe(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.PROTECT)
    composicao = models.ForeignKey(ComposicaoEquipe, on_delete=models.CASCADE, related_name="funcoes")
    funcao = models.ForeignKey(Funcao, on_delete=models.PROTECT)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Salário")
    quantidade_funcionarios = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    periculosidade = models.BooleanField(default=False, verbose_name="Periculosidade")
    horas_extras_50 = models.PositiveIntegerField(default=0, verbose_name="Horas Extras 50%")
    horas_extras_100 = models.PositiveIntegerField(default=0, verbose_name="Horas Extras 100%")
    horas_sobreaviso = models.PositiveIntegerField(default=0, verbose_name="Horas de Sobreaviso (1/3)")
    horas_prontidao = models.PositiveIntegerField(default=0, verbose_name="Horas de Prontidão (2/3)")
    horas_adicional_noturno = models.PositiveIntegerField(default=0, verbose_name="Horas Adicional Noturno")
    outros_custos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Outros Custos")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['contrato', 'composicao', 'funcao'], name='unique_funcao_por_composicao')
        ]


    def save(self, *args, **kwargs):
        # Só sobrescreve o salário se não tiver um valor definido
        if self.salario == 0 or self.salario is None:
            self.salario = self.funcao.salario
        super().save(*args, **kwargs)
