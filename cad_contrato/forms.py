from django import forms
from .models import CadastroContrato, Regional

class CadastroContratoForm(forms.ModelForm):
    inicio_vigencia_contrato = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'})
    )
    fim_vigencia_contrato = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'})
    )

    class Meta:
        model = CadastroContrato
        fields = '__all__'

class RegionalForm(forms.ModelForm):
    class Meta:
        model = Regional
        fields = ['nome', 'municipio']  # contrato removido
        labels = {
            'nome': 'Nome da Regional',
            'municipio': 'Município',
        }

