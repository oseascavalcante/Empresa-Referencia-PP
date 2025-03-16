from django import forms
from .models import ContractConfiguration

class ContractConfigurationForm(forms.ModelForm):
    inicio_vigencia_contrato = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'})
    )
    fim_vigencia_contrato = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control datepicker', 'autocomplete': 'off'})
    )

    class Meta:
        model = ContractConfiguration
        fields = '__all__'
