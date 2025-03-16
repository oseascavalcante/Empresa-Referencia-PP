from django.db import models
from cad_contrato.models import ContractConfiguration  # Importando a model do outro app
import uuid

class Equipe(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


class Funcao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nome} - R$ {self.salario}"

#Cadastro das equipes
class ComposicaoEquipe(models.Model):
    composicao_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contrato = models.ForeignKey(ContractConfiguration, on_delete=models.PROTECT)
    equipe = models.ForeignKey(Equipe, on_delete=models.PROTECT)
    quantidade_equipes = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_mobilizacao = models.DateField(default='2025-01-01')
    data_desmobilizacao = models.DateField(default='2028-01-01')
    prefixo_equipe = models.TextField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)  # Agora salva uma única vez por composição
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

#Cadastro da função
class FuncaoEquipe(models.Model):
    composicao = models.ForeignKey(ComposicaoEquipe, on_delete=models.CASCADE, related_name="funcoes")
    funcao = models.ForeignKey(Funcao, on_delete=models.PROTECT)
    quantidade_funcionarios = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    periculosidade = models.BooleanField(default=False)
    horas_extras_50 = models.PositiveIntegerField(default=0)
    horas_extras_70 = models.PositiveIntegerField(default=0)
    horas_extras_100 = models.PositiveIntegerField(default=0)
    horas_sobreaviso = models.PositiveIntegerField(default=0)
    horas_adicional_noturno = models.PositiveIntegerField(default=0)
    outros_custos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
