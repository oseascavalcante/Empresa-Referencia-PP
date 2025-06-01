# mao_obra/signals.py

from decimal import Decimal
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

@receiver(post_save, sender=CalcGrupoAEncargos)
@receiver(post_save, sender=CalcGrupoBIndenizacoes)
@receiver(post_save, sender=CalcGrupoCSubstituicoes)
def atualizar_encargos_centralizados(sender, instance, **kwargs):
    """
    Atualiza os totais na tabela EncargosSociaisCentralizados para o contrato especificado.
    """
    contrato = instance.contrato  # Obtém o contrato associado ao registro salvo
    try:
        # Obtém ou cria o registro de EncargosSociaisCentralizados para o contrato
        encargos, _ = EncargosSociaisCentralizados.objects.get_or_create(contrato=contrato)

        # Busca os valores diretamente dos modelos relacionados
        grupo_a = CalcGrupoAEncargos.objects.filter(contrato=contrato).first()
        grupo_b = CalcGrupoBIndenizacoes.objects.filter(contrato=contrato).first()
        grupo_c = CalcGrupoCSubstituicoes.objects.filter(contrato=contrato).first()
        grupo_d = CalcGrupoD.objects.filter(contrato=contrato).first()
        grupo_e = CalcGrupoE.objects.filter(contrato=contrato).first()

        # Atualiza os valores na tabela EncargosSociaisCentralizados
        encargos.total_grupo_a = grupo_a.total_grupo_a if grupo_a else Decimal('0.00')
        encargos.total_grupo_b = grupo_b.total_grupo_b if grupo_b else Decimal('0.00')
        encargos.total_grupo_c = grupo_c.total_grupo_c if grupo_c else Decimal('0.00')
        encargos.total_grupo_d = grupo_d.total_grupo_d if grupo_d else Decimal('0.00')
        encargos.total_grupo_e = grupo_e.total_grupo_e if grupo_e else Decimal('0.00')

        encargos.save()
    except Exception as e:
        print(f"Erro ao atualizar EncargosSociaisCentralizados: {e}")