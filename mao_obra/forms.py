from django import forms
from .models import GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes, BeneficiosColaborador


class GrupoAEncargosForm(forms.ModelForm):
    class Meta:
        model = GrupoAEncargos
        fields = ['inss', 'incra', 'sebrae', 'senai', 'sesi', 'sal_educacao', 'rat','fap', 'fgts', 'dec_salario', 'abono_ferias']

class GrupoBIndenizacoesForm(forms.ModelForm):
    class Meta:
        model = GrupoBIndenizacoes
        fields = ['demissoes', 'meses_emprego', 'multa_fgts']

class GrupoCSubstituicoesForm(forms.ModelForm):
    class Meta:
        model = GrupoCSubstituicoes
        fields = ['tipo_reserva_tecnica', 'hras_trab_semana', 'dias_trabalho_semana', 'feriados_fixos','feriados_moveis', 'dias_falta_ano']


class BeneficiosColaboradorForm(forms.ModelForm):
    class Meta:
        model = BeneficiosColaborador
        fields = ['assistencia_medica_odonto', 'exames_periodicos', 'refeicao', 'transporte', 'outros_custos']
        widgets = {
            'assistencia_medica_odonto': forms.NumberInput(attrs={'class': 'form-control'}),
            'exames_periodicos': forms.NumberInput(attrs={'class': 'form-control'}),
            'refeicao': forms.NumberInput(attrs={'class': 'form-control'}),
            'transporte': forms.NumberInput(attrs={'class': 'form-control'}),
            'outros_custos': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'assistencia_medica_odonto': 'Assistência Médica Odontológica',
            'exames_periodicos': 'Exames Periódicos (um por ano)',
            'refeicao': 'Refeição',
            'transporte': 'Transporte',
            'outros_custos': 'Outros Custos',
        }
