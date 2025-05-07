from django import forms
from django.db import models  # Importa os campos do Django corretamente
from cad_contrato import models as cad_contrato_models
from .models import GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes, BeneficiosColaborador

class GrupoAEncargosForm(forms.ModelForm):
    class Meta:
        model = GrupoAEncargos
        fields = [
            'forma_tributacao',
            'percentual_cprb',
            'inss', 'incra', 'sebrae', 'senai', 'sesi', 'sal_educacao',
            'rat', 'fap', 'fgts', 'dec_salario', 'abono_ferias'
        ]
        widgets = {
            'percentual_cprb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        forma = cleaned_data.get("forma_tributacao")

        if forma == "cprb":
            # Zera o INSS se estiver em regime de desoneração
            cleaned_data["inss"] = 0.00

        return cleaned_data

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
        exclude = ['total', 'contrato']  # Exclui campo de chave estrangeira
        widgets = {
            field.name: forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
            for field in model._meta.fields
            if isinstance(field, (models.DecimalField, models.IntegerField)) and field.name not in ['total', 'contrato']
        }

