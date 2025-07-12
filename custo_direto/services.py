from decimal import Decimal

from cadastro_equipe.models import FuncaoEquipe
from .models import CustoDiretoFuncao, CustoDireto
from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador
from decimal import Decimal

def calcular_custo_funcao(funcao_equipe, contrato, encargos=None, beneficios=Decimal('0.00')):
    """
    Serviço para calcular o custo direto de uma função no contrato.
    """
    salario_base = funcao_equipe.salario
    quantidade_funcionarios = funcao_equipe.quantidade_funcionarios

    # Verifica se a quantidade de funcionários é maior que zero
    if quantidade_funcionarios <= 0:
        return None  # Não salva no banco de dados

    adicional_periculosidade = salario_base * Decimal('0.30') if funcao_equipe.periculosidade else Decimal('0')
    salario_hora = (salario_base + adicional_periculosidade) / Decimal('220')
    salario_hora_sem_periculosidade = salario_base / Decimal('220')

    valor_horas_extras_50 = salario_hora * Decimal('1.5') * funcao_equipe.horas_extras_50
    valor_horas_extras_100 = salario_hora * Decimal('2.0') * funcao_equipe.horas_extras_100
    
    valor_adicional_noturno = salario_hora_sem_periculosidade * Decimal('0.2') * Decimal('1.1428') * funcao_equipe.horas_adicional_noturno
    valor_prontidao = salario_hora_sem_periculosidade * funcao_equipe.horas_prontidao * Decimal('0.67')
    valor_sobreaviso = salario_hora_sem_periculosidade * funcao_equipe.horas_sobreaviso * Decimal('0.33')

    # Busca ou cria o custo direto da função
    custo_funcao, _ = CustoDiretoFuncao.objects.get_or_create(
        contrato=contrato,
        regional=funcao_equipe.composicao.regional,
        escopo=funcao_equipe.composicao.escopo,
        composicao=funcao_equipe.composicao,
        funcao=funcao_equipe.funcao,
        defaults={
            'quantidade_funcionarios': quantidade_funcionarios,
            'salario_base': salario_base
        }
    )

    # Atualiza os valores
    custo_funcao.quantidade_funcionarios = quantidade_funcionarios
    custo_funcao.salario_base = salario_base
    custo_funcao.adicional_periculosidade = adicional_periculosidade
    custo_funcao.valor_horas_extras_50 = valor_horas_extras_50
    custo_funcao.valor_horas_extras_100 = valor_horas_extras_100
    custo_funcao.valor_adicional_noturno = valor_adicional_noturno
    custo_funcao.valor_prontidao = valor_prontidao
    custo_funcao.valor_sobreaviso = valor_sobreaviso
    custo_funcao.outros_custos = funcao_equipe.outros_custos
    custo_funcao.beneficios = beneficios

    if encargos:
        custo_funcao.percentual_grupo_a = encargos.total_grupo_a
        custo_funcao.percentual_grupo_b = encargos.total_grupo_b
        custo_funcao.percentual_grupo_c = encargos.total_grupo_c
        custo_funcao.percentual_grupo_d = encargos.total_grupo_d
        custo_funcao.percentual_grupo_e = encargos.total_grupo_e

    custo_funcao.calcular_custo_total()
    custo_funcao.save()

    return custo_funcao


def recalcular_custo_contrato(contrato):
    """
    Recalcula os custos diretos por função vinculados ao contrato.
    Atualiza os registros de CustoDiretoFuncao com novos valores de benefícios.
    """
    # Verifica se há benefícios cadastrados para o contrato
    beneficios = BeneficiosColaborador.objects.filter(contrato=contrato).first()
    if not beneficios:
        return  # Sem benefícios definidos, não há o que recalcular

    # Para cada função vinculada ao contrato, recalcula os valores
    funcoes = CustoDiretoFuncao.objects.filter(contrato=contrato)

    for funcao in funcoes:
        # Recalcula benefícios com base na função e contrato
        from mao_obra.services import BeneficioCustoDiretoService
        funcao.beneficios = BeneficioCustoDiretoService.calcular_beneficios_por_funcao(
            contrato=contrato,
            salario_base_funcao=funcao.salario_base
        )

        funcao.calcular_custo_total()
        funcao.save()
