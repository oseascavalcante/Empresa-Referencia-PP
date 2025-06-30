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
        exclude = ['contrato']

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop('contrato', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        contrato = self.contrato
        if contrato and nome and Regional.objects.filter(contrato=contrato, nome=nome).exists():
            raise forms.ValidationError("Já existe uma regional com esse nome para este contrato.")
        return cleaned_data