from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from cadastro_equipe.models import FuncaoEquipe
from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador
from custo_direto.services import recalcular_custo_contrato

@receiver(post_save, sender=FuncaoEquipe)
@receiver(post_delete, sender=FuncaoEquipe)
def atualizar_custo_contrato_funcao(sender, instance, **kwargs):
    """
    Recalcula o custo direto do contrato ao salvar ou deletar uma função de equipe.
    """
    contrato = instance.contrato
    if contrato:
        recalcular_custo_contrato(contrato)

@receiver(post_save, sender=EncargosSociaisCentralizados)
def atualizar_custo_contrato_encargos(sender, instance, **kwargs):
    """
    Recalcula o custo direto do contrato ao alterar encargos sociais.
    """
    contrato = instance.contrato
    if contrato:
        recalcular_custo_contrato(contrato)

@receiver(post_save, sender=BeneficiosColaborador)
def atualizar_custo_contrato_beneficios(sender, instance, **kwargs):
    """
    Recalcula o custo direto do contrato ao alterar benefícios.
    """
    contrato = instance.contrato
    if contrato:
        recalcular_custo_contrato(contrato)
