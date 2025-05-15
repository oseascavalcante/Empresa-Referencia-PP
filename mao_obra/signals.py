# mao_obra/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from cad_contrato.models import CadastroContrato
from mao_obra.models import (
    CalcGrupoAEncargos, CalcGrupoBIndenizacoes, CalcGrupoCSubstituicoes,
    CalcGrupoD, CalcGrupoE, EncargosSociaisCentralizados,
    GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes
)
from mao_obra.services import GrupoCalculationsService

@receiver(post_save, sender=GrupoAEncargos)
@receiver(post_save, sender=GrupoBIndenizacoes)
@receiver(post_save, sender=GrupoCSubstituicoes)
def recalcular_grupos_ao_salvar_grupo_abc(sender, instance, **kwargs):
    """
    Recalcula todos os grupos quando os dados de GrupoA, GrupoB ou GrupoC forem alterados.
    """
    contrato = instance.contrato
    GrupoCalculationsService.calcular_todos_grupos(contrato.pk)


@receiver(post_save, sender=CalcGrupoE)
def atualizar_encargos_sociais_centralizados(sender, instance, **kwargs):
    contrato = instance.contrato
    try:
        encargos_centralizados = EncargosSociaisCentralizados.objects.get(contrato_id=contrato.pk)
        encargos_centralizados.atualizar_totais()
    except EncargosSociaisCentralizados.DoesNotExist:
        pass


