from decimal import Decimal, InvalidOperation
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
                print("GA -- Instância de Grupo A não encontrada para a contrato.")
                return
            
            calc_grupo_a, created = CalcGrupoAEncargos.objects.update_or_create(
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
                calc_grupo_a.cpp + Decimal(grupo_a.fgts) +
                Decimal(grupo_a.dec_salario) + Decimal(grupo_a.abono_ferias) +
                calc_grupo_a.cpp_fgts_sal_abono
            )
            calc_grupo_a.save()
           
        except Exception as e:
            print(f"GA -- Erro inesperado ao calcular CalcGrupoAEncargos: {e}")


    @staticmethod
    def calcular_grupo_b(contrato):
        try:
            dados_a = GrupoAEncargos.objects.filter(contrato=contrato).first()
            if not dados_a:
                raise ValueError("GB -- Instância de GrupoAEncargos não encontrada para a licitação.")

            grupo_b = GrupoBIndenizacoes.objects.filter(contrato=contrato).first()
            if not grupo_b:
                print("GB -- Instância de Grupo B não encontrada para a licitação.")
                return

            calc_grupo_b, created = CalcGrupoBIndenizacoes.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )


            calc_grupo_b.ed = Decimal(grupo_b.demissoes)
            calc_grupo_b.me = Decimal(grupo_b.meses_emprego)
            calc_grupo_b.percentual_multa_fgts = Decimal(grupo_b.multa_fgts)

            aux_ap = min(Decimal(2), calc_grupo_b.me / Decimal(120))
            calc_aux = Decimal(grupo_b.multa_fgts) * (
                Decimal(dados_a.fgts) +
                (Decimal(dados_a.fgts) *
                 (Decimal(dados_a.dec_salario * 100) + Decimal(dados_a.abono_ferias * 100)))
            ) * Decimal(calc_grupo_b.ed / 10000000)

            calc_grupo_b.multa_fgts = calc_aux
            calc_grupo_b.aviso_previo_indenizado = (calc_grupo_b.ed * (Decimal(1) + aux_ap)) / calc_grupo_b.me
            calc_grupo_b.fgts_sobre_aviso_previo = Decimal(dados_a.fgts) * calc_grupo_b.aviso_previo_indenizado / Decimal(100)
            calc_grupo_b.total_grupo_b = (
                calc_grupo_b.multa_fgts + calc_grupo_b.aviso_previo_indenizado + calc_grupo_b.fgts_sobre_aviso_previo
            )

            calc_grupo_b.save()
        except Exception as e:
            print(f"GB -- Erro ao calcular CalcGrupoBIndenizacoes: {e}")

    @staticmethod
    def calcular_grupo_c(contrato):
        try:
            
            grupo_c = GrupoCSubstituicoes.objects.filter(contrato=contrato).first()
            if not grupo_c:
                print("GC -- Instância de Grupo C não encontrada para a licitação.")
                return

            calc_grupo_c, created = CalcGrupoCSubstituicoes.objects.update_or_create(
                contrato=contrato,
                defaults={}
            )

            calc_grupo_c.dias_faltas_ano = grupo_c.dias_falta_ano
            calc_grupo_c.horas_trab_semana = grupo_c.hras_trab_semana
            calc_grupo_c.horas_feriados_ferias = Decimal(Decimal(grupo_c.hras_trab_semana/grupo_c.dias_trabalho_semana)*
                                          Decimal(grupo_c.feriados_fixos + Decimal(grupo_c.dias_trabalho_semana / 7*grupo_c.feriados_moveis )))/12
            
 
            calc_grupo_c.horas_trab_ano = (
                Decimal(grupo_c.hras_trab_semana) * Decimal(365.25 / 7) -
                (Decimal(grupo_c.hras_trab_semana) / Decimal(grupo_c.dias_trabalho_semana)) *
                (Decimal(grupo_c.feriados_fixos) + (Decimal(grupo_c.dias_trabalho_semana) / 7 * grupo_c.feriados_moveis))
            )

            calc_grupo_c.semanas_ferias = Decimal(30) / Decimal(7)
            calc_grupo_c.horas_trab_dia = Decimal(grupo_c.hras_trab_semana) / Decimal(grupo_c.dias_trabalho_semana)
            calc_grupo_c.horas_ausencia_ferias = (
                Decimal(grupo_c.hras_trab_semana) * calc_grupo_c.semanas_ferias - calc_grupo_c.horas_feriados_ferias
            )
            
            calc_grupo_c.horas_faltas_justificadas_ano = calc_grupo_c.horas_ausencia_ferias + (Decimal(grupo_c.dias_falta_ano) * calc_grupo_c.horas_trab_dia)
            
            calc_grupo_c.total_grupo_c = (
                100 * calc_grupo_c.horas_faltas_justificadas_ano /
                (calc_grupo_c.horas_trab_ano - calc_grupo_c.horas_faltas_justificadas_ano)
            )
 

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
                print("GD -- Instâncias de cálculo para Grupo A, B ou C não encontradas.")
                return

            calc_grupo_d, _ = CalcGrupoD.objects.update_or_create(
                contrato=contrato
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
                print("GE -- Instâncias de cálculo para Grupo A, B, C ou D não encontradas.")
                return

            calc_grupo_e, _ = CalcGrupoE.objects.update_or_create(
                contrato=contrato
            )

            calc_grupo_e.total_grupo_e = calc_a.total_grupo_a + calc_b.total_grupo_b + calc_c.total_grupo_c + calc_d.total_grupo_d

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





