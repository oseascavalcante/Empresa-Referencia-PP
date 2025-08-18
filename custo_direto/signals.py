from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from cadastro_equipe.models import FuncaoEquipe
from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador
from .services import calcular_custo_funcao, recalcular_custo_contrato

@receiver(post_save, sender=FuncaoEquipe)
def criar_custo_direto_funcao(sender, instance, created, **kwargs):
    """
    Cria ou atualiza o custo direto quando uma FuncaoEquipe é salva.
    """
    contrato = instance.contrato
    
    if contrato and instance.quantidade_funcionarios > 0:
        try:
            # Busca encargos sociais consolidados
            encargos = EncargosSociaisCentralizados.objects.filter(contrato=contrato).first()
            
            # Busca benefícios do contrato
            beneficios = BeneficiosColaborador.objects.filter(contrato=contrato).first()
            beneficios_valor = 0
            if beneficios:
                from mao_obra.services import BeneficioCustoDiretoService
                beneficios_valor = BeneficioCustoDiretoService.calcular_beneficios_por_funcao(
                    contrato=contrato,
                    salario_base_funcao=instance.salario
                )
            
            # Calcula o custo direto da função
            custo_funcao = calcular_custo_funcao(
                funcao_equipe=instance,
                contrato=contrato,
                encargos=encargos,
                beneficios=beneficios_valor
            )
            
            print(f"[OK] Custo direto calculado: {custo_funcao}")
            
        except Exception as e:
            print(f"[ERRO] Erro ao calcular custo direto: {e}")

@receiver(post_delete, sender=FuncaoEquipe)
def remover_custo_direto_funcao(sender, instance, **kwargs):
    """
    Remove o custo direto quando uma FuncaoEquipe é excluída.
    """
    from .models import CustoDiretoFuncao
    
    try:
        # Remove o registro de custo direto relacionado
        CustoDiretoFuncao.objects.filter(
            contrato=instance.contrato,
            composicao=instance.composicao,
            funcao=instance.funcao
        ).delete()
        print(f"[OK] Custo direto removido para {instance}")
    except Exception as e:
        print(f"[ERRO] Erro ao remover custo direto: {e}")

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