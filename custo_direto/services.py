from decimal import Decimal
from .models import CustoDiretoFuncao, CustoDireto
from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador
from decimal import Decimal

def calcular_custo_funcao(funcao_equipe, contrato, encargos, beneficios):
    """
    Serviço para calcular o custo direto de uma função no contrato.
    """
    salario_base = funcao_equipe.salario
    adicional_periculosidade = salario_base * Decimal('0.30') if funcao_equipe.periculosidade else Decimal('0')

    salario_hora = salario_base / Decimal('220')  # Assumindo 220h mensais
    valor_horas_extras_50 = salario_hora * Decimal('1.5') * funcao_equipe.horas_extras_50
    valor_horas_extras_100 = salario_hora * Decimal('2.0') * funcao_equipe.horas_extras_100

    valor_adicional_noturno = salario_hora * Decimal('0.2') * funcao_equipe.horas_adicional_noturno
    valor_prontidao = salario_hora * funcao_equipe.horas_prontidao
    valor_sobreaviso = salario_hora * funcao_equipe.horas_sobreaviso

    custo_funcao = CustoDiretoFuncao.objects.create(
        contrato=contrato,
        funcao_equipe=funcao_equipe,
        salario_base=salario_base,
        adicional_periculosidade=adicional_periculosidade,
        valor_horas_extras_50=valor_horas_extras_50,
        valor_horas_extras_100=valor_horas_extras_100,
        valor_adicional_noturno=valor_adicional_noturno,
        valor_prontidao=valor_prontidao,
        valor_sobreaviso=valor_sobreaviso,
        encargos_sociais=encargos,
        beneficios=beneficios
    )

    custo_funcao.calcular_custo_total()
    custo_funcao.save()

    return custo_funcao


def recalcular_custo_contrato(contrato):
    from .models import CustoDiretoFuncao, CustoDireto
    from cadastro_equipe.models import FuncaoEquipe
    from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador

    from decimal import Decimal

    try:
        encargos = contrato.encargos_centralizados
    except EncargosSociaisCentralizados.DoesNotExist:
        encargos = None

    try:
        beneficios = BeneficiosColaborador.objects.get(contrato=contrato).total
    except BeneficiosColaborador.DoesNotExist:
        beneficios = Decimal('0.00')

    for funcao in FuncaoEquipe.objects.filter(contrato=contrato):
        custo_funcao, created = CustoDiretoFuncao.objects.get_or_create(
            contrato=contrato,
            funcao_equipe=funcao,
            defaults={
                'quantidade_funcionarios': funcao.quantidade_funcionarios,
                'salario_base': funcao.salario
            }
        )

        salario_base = funcao.salario
        quantidade_funcionarios = funcao.quantidade_funcionarios

        adicional_periculosidade = salario_base * Decimal('0.30') if funcao.periculosidade else Decimal('0')
        salario_hora = salario_base / Decimal('220')

        valor_horas_extras_50 = salario_hora * Decimal('1.5') * funcao.horas_extras_50
        valor_horas_extras_100 = salario_hora * Decimal('2.0') * funcao.horas_extras_100
        valor_adicional_noturno = salario_hora * Decimal('0.2') * funcao.horas_adicional_noturno
        valor_prontidao = salario_hora * funcao.horas_prontidao
        valor_sobreaviso = salario_hora * funcao.horas_sobreaviso

        custo_funcao.quantidade_funcionarios = quantidade_funcionarios
        custo_funcao.salario_base = salario_base
        custo_funcao.adicional_periculosidade = adicional_periculosidade
        custo_funcao.valor_horas_extras_50 = valor_horas_extras_50
        custo_funcao.valor_horas_extras_100 = valor_horas_extras_100
        custo_funcao.valor_adicional_noturno = valor_adicional_noturno
        custo_funcao.valor_prontidao = valor_prontidao
        custo_funcao.valor_sobreaviso = valor_sobreaviso
        custo_funcao.beneficios = beneficios

        if encargos:
            custo_funcao.percentual_grupo_a = encargos.total_grupo_a
            custo_funcao.percentual_grupo_b = encargos.total_grupo_b
            custo_funcao.percentual_grupo_c = encargos.total_grupo_c
            custo_funcao.percentual_grupo_d = encargos.total_grupo_d
            custo_funcao.percentual_grupo_e = encargos.total_grupo_e

        custo_funcao.calcular_custo_total()
        custo_funcao.save()

    custo_contrato, created = CustoDireto.objects.get_or_create(contrato=contrato)
    custo_contrato.calcular_custo_total()
    custo_contrato.save()
    return custo_contrato

