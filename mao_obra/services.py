from decimal import Decimal
import decimal
from .models import (
    GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes,
    CalcGrupoAEncargos, CalcGrupoBIndenizacoes, CalcGrupoCSubstituicoes,
    CalcGrupoD, CalcGrupoE
)

class GrupoCalculationsService:
    @staticmethod
    def calcular_grupo_a(contrato):
        try:
            grupo_a = GrupoAEncargos.objects.filter(contrato=contrato).first()
            if not grupo_a:
                print(f"GA -- Instância de Grupo A não encontrada para o contrato {contrato.id}.")
                return

            calc_grupo_a, _ = CalcGrupoAEncargos.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            soma_seis_primeiros = (
                Decimal(grupo_a.inss) +
                Decimal(grupo_a.incra) +
                Decimal(grupo_a.sebrae) +
                Decimal(grupo_a.senai) +
                Decimal(grupo_a.sesi) +
                Decimal(grupo_a.sal_educacao)
            )

            calc_grupo_a.cpp = soma_seis_primeiros + (Decimal(grupo_a.rat) * Decimal(grupo_a.fap))
            calc_grupo_a.cpp_fgts_sal_abono = (
                (calc_grupo_a.cpp + Decimal(grupo_a.fgts)) *
                (Decimal(grupo_a.dec_salario) + Decimal(grupo_a.abono_ferias)) / Decimal(100)
            )
            calc_grupo_a.total_grupo_a = (
                calc_grupo_a.cpp + 
                Decimal(grupo_a.fgts) +
                Decimal(grupo_a.dec_salario) + 
                Decimal(grupo_a.abono_ferias) +
                calc_grupo_a.cpp_fgts_sal_abono
            )
            calc_grupo_a.save()
        except Exception as e:
            print(f"GA -- Erro inesperado ao calcular CalcGrupoAEncargos: {e}")

    @staticmethod
    def calcular_grupo_b(contrato):
        try:
            grupo_a = GrupoAEncargos.objects.filter(contrato=contrato).first()
            grupo_b = GrupoBIndenizacoes.objects.filter(contrato=contrato).first()
            
            if not grupo_a or not grupo_b:
                print(f"GB -- Instância de Grupo A ou Grupo B não encontrada para o contrato {contrato.id}.")
                return

            calc_grupo_b, _ = CalcGrupoBIndenizacoes.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            # Dados do Grupo A
            fgts = Decimal(grupo_a.fgts/100 or 0)
            dec_terc_salario = Decimal(grupo_a.dec_salario/100 or 0)
            abono_ferias = Decimal(grupo_a.abono_ferias/100 or 0)

            # Dados do Grupo B
            percentual_multa_fgts = Decimal(grupo_b.multa_fgts/100 or 0)
            ed = Decimal(grupo_b.demissoes/100 or 0)
            me = Decimal(grupo_b.meses_emprego or 1)  # Evitar divisão por zero

            # Verificar se os valores são válidos
            if me <= 0:
                print(f"GB -- Valor inválido para ME (meses_emprego): {me}")
                return

            # Cálculos
            calc_grupo_b.multa_fgts = 100 * (
                percentual_multa_fgts * (
                    fgts + fgts * (dec_terc_salario + abono_ferias)
                ) * ed
            )
            
            calc_grupo_b.aviso_previo_indenizado = 100 * ed * (1 + (2 if me / 120 > 2 else me / 120)) / me
            calc_grupo_b.fgts_sobre_aviso_previo = fgts * calc_grupo_b.aviso_previo_indenizado

            calc_grupo_b.total_grupo_b = (
                calc_grupo_b.multa_fgts +
                calc_grupo_b.fgts_sobre_aviso_previo +
                calc_grupo_b.aviso_previo_indenizado
            )

            # Salvar os resultados
            calc_grupo_b.save()
        except decimal.InvalidOperation as e:
            print(f"GB -- Erro de operação inválida ao calcular CalcGrupoBIndenizacoes: {e}")
                
        except Exception as e:
            print(f"GB -- Erro inesperado ao calcular CalcGrupoBIndenizacoes: {e}")

    @staticmethod
    def calcular_grupo_c(contrato):
        try:
            grupo_c = GrupoCSubstituicoes.objects.filter(contrato=contrato).first()
            if not grupo_c:
                print(f"GC -- Instância de Grupo C não encontrada para o contrato {contrato.id}.")
                return

            calc_grupo_c, _ = CalcGrupoCSubstituicoes.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            calc_grupo_c.dias_faltas_ano = grupo_c.dias_falta_ano
            calc_grupo_c.horas_trab_semana = grupo_c.hras_trab_semana
            calc_grupo_c.total_grupo_c = (
                Decimal(grupo_c.dias_falta_ano) * Decimal(grupo_c.hras_trab_semana)
            )
            hras_feriados_ano = (grupo_c.hras_trab_semana / grupo_c.dias_trabalho_semana) * (grupo_c.feriados_fixos + (grupo_c.dias_trabalho_semana / 7)* grupo_c.feriados_moveis) 
            
            #Horas trabalhas no ano = HTA
            HTA = grupo_c.hras_trab_semana * (365.25/7) - hras_feriados_ano
            calc_grupo_c.horas_trab_ano = HTA
                       
            #Horas de ausência nas férias = HAF 
            HAF = grupo_c.hras_trab_semana * (30/7) - (hras_feriados_ano / 12)            
            
            #HTD = horas trabalhadas no dia
            HDT = grupo_c.hras_trab_semana / grupo_c.dias_trabalho_semana
            calc_grupo_c.horas_trab_dia = HDT
            
            
            #Horas de faltas justificadas no ano = HFJA = HAF + DF x HTD ---->
            HFJA = HAF + (grupo_c.dias_falta_ano * HDT)
            calc_grupo_c.horas_faltas_justificadas_ano = HFJA
            
            #Total grupo C = HFJA ÷ (HTA - HFJA)
            calc_grupo_c.total_grupo_c = (HFJA / (HTA - HFJA)) * 100
            

            calc_grupo_c.save()
        except Exception as e:
            print(f"GC -- Erro ao calcular CalcGrupoCSubstituicoes: {e}")

    @staticmethod
    def calcular_grupo_d(contrato):
        try:
            calc_grupo_a = CalcGrupoAEncargos.objects.filter(contrato=contrato).first()
            calc_grupo_b = CalcGrupoBIndenizacoes.objects.filter(contrato=contrato).first()
            calc_grupo_c = CalcGrupoCSubstituicoes.objects.filter(contrato=contrato).first()

            if not calc_grupo_a or not calc_grupo_b or not calc_grupo_c:
                print(f"GD -- Faltam cálculos A, B ou C para contrato {contrato.id}.")
                return

            calc_grupo_d, _ = CalcGrupoD.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            calc_grupo_d.total_grupo_d = (
                calc_grupo_c.total_grupo_c * (calc_grupo_a.total_grupo_a + calc_grupo_b.total_grupo_b) / Decimal(100)
            )
            calc_grupo_d.save()
        except Exception as e:
            print(f"GD -- Erro ao calcular CalcGrupoD: {e}")

    @staticmethod
    def calcular_grupo_e(contrato):
        try:
            calc_a = CalcGrupoAEncargos.objects.filter(contrato=contrato).first()
            calc_b = CalcGrupoBIndenizacoes.objects.filter(contrato=contrato).first()
            calc_c = CalcGrupoCSubstituicoes.objects.filter(contrato=contrato).first()
            calc_d = CalcGrupoD.objects.filter(contrato=contrato).first()

            if not calc_a or not calc_b or not calc_c or not calc_d:
                print(f"GE -- Faltam dados dos grupos A, B, C ou D para contrato {contrato.id}.")
                return
            
            calc_grupo_e, _ = CalcGrupoE.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )
            
            calc_grupo_e.total_grupo_e = (
                calc_a.total_grupo_a +
                calc_b.total_grupo_b +
                calc_c.total_grupo_c +
                calc_d.total_grupo_d
            )


            calc_grupo_e.save()
        except Exception as e:
            print(f"GE -- Erro ao calcular CalcGrupoE: {e}")

    @staticmethod
    def calcular_todos_grupos(contrato):
        GrupoCalculationsService.calcular_grupo_a(contrato)
        GrupoCalculationsService.calcular_grupo_b(contrato)
        GrupoCalculationsService.calcular_grupo_c(contrato)
        GrupoCalculationsService.calcular_grupo_d(contrato)
        GrupoCalculationsService.calcular_grupo_e(contrato)
