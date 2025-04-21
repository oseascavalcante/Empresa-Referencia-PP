from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes
from .services import GrupoCalculationsService

@receiver(post_save, sender=GrupoAEncargos)
@receiver(post_save, sender=GrupoBIndenizacoes)
@receiver(post_save, sender=GrupoCSubstituicoes)
def calcular_grupos(sender, instance, **kwargs):
    """
    Dispara os cálculos sempre que um objeto de GrupoAEncargos, GrupoBIndenizacoes
    ou GrupoCSubstituicoes for salvo.
    """
    contrato = instance.contrato  # Obtém o contrato relacionado ao objeto salvo
    GrupoCalculationsService.calcular_todos_grupos(contrato)