from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    CalcGrupoAEncargos, CalcGrupoBIndenizacoes, CalcGrupoCSubstituicoes,
    CalcGrupoD, CalcGrupoE, EncargosSociaisCentralizados,
    GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes
)
from .services import GrupoCalculationsService

@receiver(post_save, sender=GrupoAEncargos)
@receiver(post_save, sender=GrupoBIndenizacoes)
@receiver(post_save, sender=GrupoCSubstituicoes)
def calcular_grupos(sender, instance, **kwargs):
    """
    Dispara os cálculos sempre que um objeto de GrupoAEncargos, GrupoBIndenizacoes
    ou GrupoCSubstituicoes for salvo.
    """
    contrato_id = instance.contrato.pk  # Passa apenas o ID
    GrupoCalculationsService.calcular_todos_grupos(contrato_id)

@receiver(post_save, sender=CalcGrupoAEncargos)
@receiver(post_save, sender=CalcGrupoBIndenizacoes)
@receiver(post_save, sender=CalcGrupoCSubstituicoes)
@receiver(post_save, sender=CalcGrupoD)
@receiver(post_save, sender=CalcGrupoE)
def atualizar_encargos_centralizados(sender, instance, **kwargs):
    contrato = instance.contrato
    encargos_centralizados, created = EncargosSociaisCentralizados.objects.get_or_create(contrato=contrato)
    encargos_centralizados.atualizar_totais()
