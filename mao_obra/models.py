from django.db import models
from decimal import Decimal, InvalidOperation
from cadastro_equipe.models import Funcao
from cad_contrato.models import CadastroContrato  # Importando o modelo de contrato


class GrupoAEncargos(models.Model):
    FORMA_TRIBUTACAO_CHOICES = [
    ('cpp', 'CPP - 20% sobre a folha (Contribuição Patronal)'),
    ('cprb', 'CPRB - % sobre a receita bruta (Desoneração da Folha)'),
    ]
    # Definindo os campos do modelo   
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    forma_tributacao = models.CharField(
    max_length=5,
    choices=FORMA_TRIBUTACAO_CHOICES,
    default='cpp',
    verbose_name='Forma de Tributação (CPP ou CPRB)'
    )
    percentual_cprb = models.DecimalField(
    max_digits=5,
    decimal_places=2,
    default=4.50,
    verbose_name="CPRB (%) sobre receita bruta"
    )
    inss = models.DecimalField(max_digits=5, decimal_places=2, default=20.00, verbose_name="INSS (%)")
    incra = models.DecimalField(max_digits=5, decimal_places=2, default=0.20, verbose_name="INCRA (%)")
    sebrae = models.DecimalField(max_digits=5, decimal_places=2, default=0.60,  verbose_name="SEBRAE (%)")
    senai = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,  verbose_name="SENAI (%)")
    sesi = models.DecimalField(max_digits=5, decimal_places=2, default=1.50,  verbose_name="SESI (%)")
    sal_educacao = models.DecimalField(max_digits=10, decimal_places=2, default=2.50,  verbose_name="Salário Educação (%)")  
    rat = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        choices=[
            (1.00, '1,0%'),
            (2.00, '2,0%'),
            (3.00, '3,0%'),
        ],
        default=3.00,
        verbose_name="RAT (Riscos Ambientais do Trabalho)"
    )
    fap = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        choices=[
            (0.50, '0,5'),
            (1.00, '1,0'),
            (1.50, '1,5'),
            (2.00, '2,0'),
        ],
        default=1.00,
        verbose_name="FAP (Fator Acidentário de Prevenção)"
    )
    fgts = models.DecimalField(max_digits=5, decimal_places=2,  default=8.00, verbose_name="FGTS (%)")
    dec_salario = models.DecimalField(max_digits=5, decimal_places=2, default=8.33,  verbose_name="13 Salário (%)")
    abono_ferias = models.DecimalField(max_digits=5, decimal_places=2,  default=2.78, verbose_name="Abono de Férias (%)")


    def __str__(self):
        return f"Grupo A Encargos - ID {self.id}"

class GrupoBIndenizacoes(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    demissoes = models.DecimalField(max_digits=5, decimal_places=2,   default=100.00, verbose_name="Demissões (%)")
    meses_emprego = models.IntegerField(default=36, verbose_name="Meses no emprego")
    multa_fgts = models.DecimalField(max_digits=5, decimal_places=2, default=40.00, verbose_name="Multa do FGTS (%)")

    def __str__(self):
        return f"Grupo B Indenizações - ID {self.id}"

class GrupoCSubstituicoes(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    tipo_reserva_tecnica = models.CharField(
        max_length=3,
        choices=[('sim', 'Sim'), ('nao', 'Não')],
        verbose_name="A reserva técnica  já está sendo considerada?",
        default='sim'
    )
    
    hras_trab_semana = models.IntegerField(default=44, verbose_name="Horas trabalhadas na semana")
    dias_trabalho_semana = models.IntegerField(default=5, verbose_name="Dias de trabalho na semana")
    feriados_fixos = models.IntegerField(default=5, verbose_name="Feriados fixos no ano - ocorrem sempre nos dias de trabalho")   
    feriados_moveis = models.IntegerField(default=12, verbose_name="Feriados móveis no ano - ocorrem em qualquer dia da semana")
    dias_falta_ano = models.IntegerField(default=3, verbose_name="Dias de falta no ano")

    def __str__(self):
        return f"Grupo C Substituições - ID {self.id}"


#PARTE CALCULADA

class CalcGrupoAEncargos(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    cpp = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="CPP (Contribuição Previdenciária Patronal)")
    cpp_fgts_sal_abono = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="(CPP + FGTS) x (13 salário + abono de férias)")
    total_grupo_a = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='Total Grupo A')

    def save(self, *args, **kwargs):
        # Remove a lógica de cálculo, pois ela será tratada pela signal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"CalcGrupoAEncargos - Licitação {self.contrato.id}"


class CalcGrupoBIndenizacoes(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato

    multa_fgts = models.DecimalField(default=0, max_digits=100, decimal_places=2, verbose_name="Multa do FGTS")
    aviso_previo_indenizado = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Aviso prévio indenizado")
    fgts_sobre_aviso_previo = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="FGTS sobre aviso prévio indenizado")
    total_grupo_b = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Total Grupo B")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Apenas salva o objeto normalmente

    def __str__(self):
        return f"CalcGrupoBIndenizacoes ({self.dados_grupo_b})"

class CalcGrupoCSubstituicoes(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato

    horas_trab_ano = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Horas trabalhas no ano")
    semanas_ferias = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Semanas de férias = 30 ÷ 7")
    horas_ausencia_ferias = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Horas de ausência nas férias (HAF = HTS x SF - HFF)")
    dias_faltas_ano = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Dias de faltas no ano")
    horas_trab_semana = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Horas trabalhadas na semana")
    horas_feriados_ferias = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Horas de feriados nas férias")
    horas_trab_dia = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Horas trabalhadas no dia")
    horas_faltas_justificadas_ano = models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name="Horas de faltas justificadas no ano (HFJA = HAF + DF x HTD)")
    total_grupo_c = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Total Grupo C")
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Apenas salva o objeto normalmente

    def __str__(self):
        return f"CalcGrupoCSubstituicoes ({self.dados_grupo_c})"
        

class CalcGrupoD(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    total_grupo_d = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Total Grupo D")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Apenas salva o objeto normalmente

    def __str__(self):
        return f"CalcGrupoD - Licitação {self.contrato.id}"



class CalcGrupoE(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    total_grupo_e = models.DecimalField(default=0, max_digits=5, decimal_places=2, verbose_name="Total Grupo E")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Apenas salva o objeto normalmente

    def __str__(self):
        return f"CalcGrupoD - Licitação {self.composicao.id}"

#Gera uma tabela com os totais consolidados de cada grupo de encargos sociais
# e benefícios, para facilitar a visualização e o cálculo do custo total do contrato.
class EncargosSociaisCentralizados(models.Model):
    contrato = models.OneToOneField(CadastroContrato, on_delete=models.CASCADE, related_name="encargos_centralizados")
    total_grupo_a = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Grupo A")
    total_grupo_b = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Grupo B")
    total_grupo_c = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Grupo C")
    total_grupo_d = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Grupo D")
    total_grupo_e = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total Grupo E")

    def atualizar_totais(self):
        """
        Atualiza o total geral somando os grupos A, B, C, D e E, 
        tratando possíveis valores None de forma segura.
        """
        # Garante que todos os valores são Decimal e não None
        total_a = self.total_grupo_a if self.total_grupo_a is not None else Decimal('0.00')
        total_b = self.total_grupo_b if self.total_grupo_b is not None else Decimal('0.00')
        total_c = self.total_grupo_c if self.total_grupo_c is not None else Decimal('0.00')
        total_d = self.total_grupo_d if self.total_grupo_d is not None else Decimal('0.00')
        total_e = self.total_grupo_e if self.total_grupo_e is not None else Decimal('0.00')

        # Agora pode somar com segurança
        self.total_geral = total_a + total_b + total_c + total_d + total_e

        self.save()




class BeneficiosColaborador(models.Model):
    contrato = models.ForeignKey(CadastroContrato, on_delete=models.CASCADE)  # Vínculo com o contrato
    assistencia_medica_odonto = models.DecimalField(
        max_digits=7, decimal_places=2, default=151.00, verbose_name="Assistência médica odontológica"
    )
    exames_periodicos = models.DecimalField(
        max_digits=7, decimal_places=2, default=109.00, verbose_name="Exames periódicos (um por ano)"
    )
    refeicao = models.DecimalField(
        max_digits=7, decimal_places=2, default=398.00, verbose_name="Refeição"
    )
    cesta_basica = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00, verbose_name="Cesta básica"
    )

    alojamento = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00, verbose_name="Alojamento"
    )

    seguro_vida = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00, verbose_name="Seguro de vida"
    )
    previdencia_privada = models.DecimalField(
        max_digits=7, decimal_places=2, default=0.00, verbose_name="Plano de previdência privada"
    )
    transporte = models.DecimalField(
        max_digits=7, decimal_places=2, default=278.00, verbose_name="Transporte"
    )
    percentual_participacao_transporte = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=6.00,
        verbose_name="Participação do trabalhador no VT (%)"
    )
    dias_trabalhados_mes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=21.00,
        verbose_name="Dias médios trabalhados no mês"
    )       
    outros_custos = models.DecimalField(max_digits=7, decimal_places=2, default=0.00, verbose_name='Outros Custos')       
    total = models.DecimalField(
        max_digits=7, decimal_places=2, default=0, verbose_name="Total"
    )
    def save(self, *args, **kwargs):
        self.total = (
            self.assistencia_medica_odonto +
            self.exames_periodicos +
            self.refeicao +
            self.transporte +
            self.outros_custos +
            self.alojamento +
            self.cesta_basica +
            self.seguro_vida +
            self.previdencia_privada
        )
        super().save(*args, **kwargs)



