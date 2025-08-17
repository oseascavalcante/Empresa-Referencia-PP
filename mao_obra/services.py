from cad_contrato.models import CadastroContrato
from decimal import Decimal
import decimal
from .models import (
    BeneficiosColaborador, GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes,
    CalcGrupoAEncargos, CalcGrupoBIndenizacoes, CalcGrupoCSubstituicoes,
    CalcGrupoD, CalcGrupoE
)

class GrupoCalculationsService:
    @staticmethod
    def calcular_grupo_a(contrato):
        """
        Calcula o Grupo A de Encargos para o contrato informado.
        """
        try:

            grupo_a = GrupoAEncargos.objects.filter(contrato=contrato).first()
            if not grupo_a:
                print(f"[AVISO] GA -- Instância de Grupo A não encontrada para o contrato {contrato.pk}.")
                return

            calc_grupo_a, _ = CalcGrupoAEncargos.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            # Função segura para conversão
            def safe_decimal(value, field_name):
                try:
                    return Decimal(str(value)) if value is not None else Decimal('0.00')
                except Exception as e:
                    print(f"Erro ao converter {field_name}: {e}")
                    return Decimal('0.00')

            # Soma dos seis primeiros encargos
            soma_seis_primeiros = (
                safe_decimal(grupo_a.inss, "inss") +
                safe_decimal(grupo_a.incra, "incra") +
                safe_decimal(grupo_a.sebrae, "sebrae") +
                safe_decimal(grupo_a.senai, "senai") +
                safe_decimal(grupo_a.sesi, "sesi") +
                safe_decimal(grupo_a.sal_educacao, "sal_educacao")
            )

            rat = safe_decimal(grupo_a.rat, "rat")
            fap = safe_decimal(grupo_a.fap, "fap")
            fgts = safe_decimal(grupo_a.fgts, "fgts")
            dec_salario = safe_decimal(grupo_a.dec_salario, "dec_salario")
            abono_ferias = safe_decimal(grupo_a.abono_ferias, "abono_ferias")

            # Cálculos principais
            calc_grupo_a.cpp = soma_seis_primeiros + (rat * fap)

            calc_grupo_a.cpp_fgts_sal_abono = (
                (calc_grupo_a.cpp + fgts) *
                (dec_salario + abono_ferias) / Decimal('100')
            )

            calc_grupo_a.total_grupo_a = (
                calc_grupo_a.cpp +
                fgts +
                dec_salario +
                abono_ferias +
                calc_grupo_a.cpp_fgts_sal_abono
            )

            calc_grupo_a.save()

        except Exception as e:
            print(f"[ERRO] GA -- Erro inesperado ao calcular CalcGrupoAEncargos: {e}")


    @staticmethod
    def calcular_grupo_b(contrato):
        """
        Calcula o Grupo B de Indenizações para o contrato informado.
        """
        try:

            grupo_a = GrupoAEncargos.objects.filter(contrato=contrato).first()
            grupo_b = GrupoBIndenizacoes.objects.filter(contrato=contrato).first()

            if not grupo_a or not grupo_b:
                print(f"[AVISO] GB -- Instância de Grupo A ou Grupo B não encontrada para contrato {contrato.pk}.")
                return

            calc_grupo_b, _ = CalcGrupoBIndenizacoes.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            # Função segura para conversão
            def safe_decimal(value, field_name):
                try:
                    return Decimal(str(value)) if value is not None else Decimal('0.00')
                except Exception as e:
                    print(f"Erro ao converter {field_name}: {e}")
                    return Decimal('0.00')

            # Dados do Grupo A
            fgts = safe_decimal(grupo_a.fgts, "fgts") / Decimal('100')
            dec_terc_salario = safe_decimal(grupo_a.dec_salario, "dec_salario") / Decimal('100')
            abono_ferias = safe_decimal(grupo_a.abono_ferias, "abono_ferias") / Decimal('100')

            # Dados do Grupo B
            percentual_multa_fgts = safe_decimal(grupo_b.multa_fgts, "multa_fgts") / Decimal('100')
            ed = safe_decimal(grupo_b.demissoes, "demissoes") / Decimal('100')
            me = grupo_b.meses_emprego or 1  # Garante que não é zero

            if me <= 0:
                print(f"[AVISO] GB -- Valor inválido para ME (meses_emprego): {me}")
                return

            # Cálculo da multa FGTS
            calc_grupo_b.multa_fgts = Decimal('100') * (
                percentual_multa_fgts * (
                    fgts + (fgts * (dec_terc_salario + abono_ferias))
                ) * ed
            )

            # Cálculo do aviso prévio indenizado
            fator_aviso_previo = (Decimal('2') if me / Decimal('120') > Decimal('2') else (Decimal(str(me)) / Decimal('120')))
            calc_grupo_b.aviso_previo_indenizado = (Decimal('100') * ed * (Decimal('1') + fator_aviso_previo)) / Decimal(str(me))

            # Cálculo do FGTS sobre aviso prévio
            calc_grupo_b.fgts_sobre_aviso_previo = fgts * calc_grupo_b.aviso_previo_indenizado

            # Total Grupo B
            calc_grupo_b.total_grupo_b = (
                calc_grupo_b.multa_fgts +
                calc_grupo_b.fgts_sobre_aviso_previo +
                calc_grupo_b.aviso_previo_indenizado
            )

            # Salva o cálculo
            calc_grupo_b.save()

        except decimal.InvalidOperation as e:
            print(f"[ERRO] GB -- Erro de operação inválida ao calcular CalcGrupoBIndenizacoes: {e}")
        except Exception as e:
            print(f"[ERRO] GB -- Erro inesperado ao calcular CalcGrupoBIndenizacoes: {e}")


    @staticmethod
    def calcular_grupo_c(contrato):
        """
        Calcula o Grupo C de Substituições para o contrato informado.
        """
        try:

            grupo_c = GrupoCSubstituicoes.objects.filter(contrato=contrato).first()
            if not grupo_c:
                print(f"[AVISO] GC -- Instância de Grupo C não encontrada para o contrato {contrato.pk}.")
                return

            calc_grupo_c, _ = CalcGrupoCSubstituicoes.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            # Função segura para conversão
            def safe_decimal(value, field_name):
                try:
                    return Decimal(str(value)) if value is not None else Decimal('0.00')
                except Exception as e:
                    print(f"Erro ao converter {field_name}: {e}")
                    return Decimal('0.00')

            # Preparação dos dados
            dias_falta_ano = safe_decimal(grupo_c.dias_falta_ano, "dias_falta_ano")
            hras_trab_semana = safe_decimal(grupo_c.hras_trab_semana, "hras_trab_semana")
            dias_trabalho_semana = safe_decimal(grupo_c.dias_trabalho_semana, "dias_trabalho_semana")
            feriados_fixos = safe_decimal(grupo_c.feriados_fixos, "feriados_fixos")
            feriados_moveis = safe_decimal(grupo_c.feriados_moveis, "feriados_moveis")

            if dias_trabalho_semana == 0:
                print(f"[AVISO] GC -- Valor inválido para dias_trabalho_semana: {dias_trabalho_semana}")
                return

            # Calculando Horas Trabalhadas no Ano (HTA)
            hras_feriados_ano = (hras_trab_semana / dias_trabalho_semana) * (
                feriados_fixos + (dias_trabalho_semana / Decimal('7')) * feriados_moveis
            )

            HTA = (hras_trab_semana * (Decimal('365.25') / Decimal('7'))) - hras_feriados_ano

            # Calculando Horas de Ausência nas Férias (HAF)
            HAF = (hras_trab_semana * (Decimal('30') / Decimal('7'))) - (hras_feriados_ano / Decimal('12'))

            # Calculando Horas Trabalhadas por Dia (HDT)
            HDT = hras_trab_semana / dias_trabalho_semana

            # Calculando Horas de Faltas Justificadas no Ano (HFJA)
            HFJA = HAF + (dias_falta_ano * HDT)

            # Preenchendo campos calculados
            calc_grupo_c.dias_faltas_ano = dias_falta_ano
            calc_grupo_c.horas_trab_semana = hras_trab_semana
            calc_grupo_c.horas_trab_ano = HTA
            calc_grupo_c.horas_trab_dia = HDT
            calc_grupo_c.horas_faltas_justificadas_ano = HFJA

            # Calculando Total Grupo C
            if (HTA - HFJA) > 0:
                calc_grupo_c.total_grupo_c = (HFJA / (HTA - HFJA)) * Decimal('100')
            else:
                print(f"[AVISO] GC -- HTA - HFJA inválido para o contrato {contrato.pk}.")
                calc_grupo_c.total_grupo_c = Decimal('0.00')

            calc_grupo_c.save()

        except Exception as e:
            print(f"[ERRO] GC -- Erro ao calcular CalcGrupoCSubstituicoes: {e}")


    @staticmethod
    def calcular_grupo_d(contrato):
        """
        Calcula o Grupo D consolidando os Grupos A, B e C para o contrato informado.
        """
        try:

            calc_grupo_a = CalcGrupoAEncargos.objects.filter(contrato=contrato).first()
            calc_grupo_b = CalcGrupoBIndenizacoes.objects.filter(contrato=contrato).first()
            calc_grupo_c = CalcGrupoCSubstituicoes.objects.filter(contrato=contrato).first()

            if not calc_grupo_a or not calc_grupo_b or not calc_grupo_c:
                print(f"[AVISO] GD -- Faltam cálculos A, B ou C para o contrato {contrato.pk}.")
                return

            calc_grupo_d, _ = CalcGrupoD.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            # Função segura para conversão
            def safe_decimal(value, field_name):
                try:
                    return Decimal(str(value)) if value is not None else Decimal('0.00')
                except Exception as e:
                    print(f"Erro ao converter {field_name}: {e}")
                    return Decimal('0.00')

            total_a = safe_decimal(calc_grupo_a.total_grupo_a, "total_grupo_a")
            total_b = safe_decimal(calc_grupo_b.total_grupo_b, "total_grupo_b")
            total_c = safe_decimal(calc_grupo_c.total_grupo_c, "total_grupo_c")

            # Cálculo do Grupo D
            calc_grupo_d.total_grupo_d = (
                total_c * (total_a + total_b) / Decimal('100')
            )

            calc_grupo_d.save()

        except Exception as e:
            print(f"[ERRO] GD -- Erro ao calcular CalcGrupoD: {e}")


    @staticmethod
    def calcular_grupo_e(contrato):
        """
        Calcula o Grupo E consolidando os Grupos A, B, C e D para o contrato informado.
        """
        try:

            calc_a = CalcGrupoAEncargos.objects.filter(contrato=contrato).first()
            calc_b = CalcGrupoBIndenizacoes.objects.filter(contrato=contrato).first()
            calc_c = CalcGrupoCSubstituicoes.objects.filter(contrato=contrato).first()
            calc_d = CalcGrupoD.objects.filter(contrato=contrato).first()

            if not calc_a or not calc_b or not calc_c or not calc_d:
                print(f"[AVISO] GE -- Faltam dados dos grupos A, B, C ou D para contrato {contrato.pk}.")
                return

            calc_grupo_e, _ = CalcGrupoE.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            # Função segura para conversão
            def safe_decimal(value, field_name):
                try:
                    return Decimal(str(value)) if value is not None else Decimal('0.00')
                except Exception as e:
                    print(f"Erro ao converter {field_name}: {e}")
                    return Decimal('0.00')

            total_a = safe_decimal(calc_a.total_grupo_a, "total_grupo_a")
            total_b = safe_decimal(calc_b.total_grupo_b, "total_grupo_b")
            total_c = safe_decimal(calc_c.total_grupo_c, "total_grupo_c")
            total_d = safe_decimal(calc_d.total_grupo_d, "total_grupo_d")

            # Cálculo do Grupo E
            calc_grupo_e.total_grupo_e = (
                total_a +
                total_b +
                total_c +
                total_d
            )

            calc_grupo_e.save()

        except Exception as e:
            print(f"[ERRO] GE -- Erro ao calcular CalcGrupoE: {e}")



    @staticmethod
    def calcular_todos_grupos(contrato_id):
        """
        Calcula todos os grupos (A, B, C, D, E) para um contrato existente.
        """
        try:
            # Verifica se o parâmetro é um ID ou um objeto CadastroContrato
            if isinstance(contrato_id, int):  # Se for um ID, busca o objeto correspondente
                contrato = CadastroContrato.objects.get(pk=contrato_id)
            else:
                contrato = contrato_id  # Caso já seja um objeto CadastroContrato


            # Agora passa o OBJETO, não o ID
            GrupoCalculationsService.calcular_grupo_a(contrato)
            GrupoCalculationsService.calcular_grupo_b(contrato)
            GrupoCalculationsService.calcular_grupo_c(contrato)
            GrupoCalculationsService.calcular_grupo_d(contrato)
            GrupoCalculationsService.calcular_grupo_e(contrato)

        except CadastroContrato.DoesNotExist:
            print(f"[ERRO] Contrato com ID {contrato_id} não encontrado. Não foi possível calcular os grupos.")

        except Exception as e:
            print(f"[ERRO] Erro inesperado ao calcular todos os grupos: {e}")

# mao_obra/services.py
class BeneficioCustoDiretoService:
    @staticmethod
    def calcular_beneficios_por_funcao(contrato, salario_base_funcao):
        """
        Calcula os benefícios totais para uma função considerando VT líquido.
        """
        beneficios = BeneficiosColaborador.objects.filter(contrato=contrato).first()
        if not beneficios:
            return Decimal('0.00')

        desconto_max = salario_base_funcao * beneficios.percentual_participacao_transporte / Decimal('100')
        desconto_aplicado = min(beneficios.transporte, desconto_max)
        vt_liquido = beneficios.transporte - desconto_aplicado

        total = (
            beneficios.assistencia_medica_odonto +
            beneficios.exames_periodicos +
            beneficios.refeicao +
            beneficios.cesta_basica +
            beneficios.alojamento +
            beneficios.seguro_vida +
            beneficios.previdencia_privada +
            beneficios.outros_custos +
            vt_liquido
        )

        return total.quantize(Decimal('0.01'))
