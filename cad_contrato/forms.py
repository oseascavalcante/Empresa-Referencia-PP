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

# forms.py
class RegionalForm(forms.ModelForm):
    class Meta:
        model = Regional
        fields = ['nome', 'municipio']

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop('contrato', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        contrato = self.contrato

        if contrato and nome:
            qs = Regional.objects.filter(contrato=contrato, nome=nome)
            # ✅ Ignora a própria instância no update
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                # opcional: atrelar o erro ao campo 'nome' (melhor UX)
                self.add_error('nome', "Já existe uma regional com esse nome para este contrato.")

        return cleaned_data
