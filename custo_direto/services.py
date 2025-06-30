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
    salario_hora = salario_base / Decimal('220')

    valor_horas_extras_50 = salario_hora * Decimal('0.5') * funcao_equipe.horas_extras_50
    valor_horas_extras_100 = salario_hora * Decimal('1.0') * funcao_equipe.horas_extras_100
    
    valor_adicional_noturno = salario_hora * Decimal('0.2') * Decimal('1.1428') * funcao_equipe.horas_adicional_noturno
    valor_prontidao = salario_hora * funcao_equipe.horas_prontidao * Decimal('0.67')
    valor_sobreaviso = salario_hora * funcao_equipe.horas_sobreaviso * Decimal('0.33')

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
    Serviço para recalcular o custo direto de todas as funções no contrato.
    """

    try:
        encargos = contrato.encargos_centralizados
    except EncargosSociaisCentralizados.DoesNotExist:
        encargos = None

    try:
        beneficios = BeneficiosColaborador.objects.get(contrato=contrato).total
    except BeneficiosColaborador.DoesNotExist:
        beneficios = Decimal('0.00')

    # Itera sobre todas as funções de equipe e recalcula o custo
    for funcao_equipe in FuncaoEquipe.objects.filter(contrato=contrato):
        calcular_custo_funcao(funcao_equipe, contrato, encargos, beneficios)

    # Recalcula o custo total do contrato
    custo_contrato, created = CustoDireto.objects.get_or_create(contrato=contrato)
    custo_contrato.calcular_custo_total()
    custo_contrato.save()

    return custo_contrato