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
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da regional'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Município'})
        }

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop('contrato', None)
        super().__init__(*args, **kwargs)
        
        # Adiciona classes de erro se existirem
        if self.errors:
            for field_name, field in self.fields.items():
                if field_name in self.errors:
                    if 'class' in field.widget.attrs:
                        field.widget.attrs['class'] += ' is-invalid'
                    else:
                        field.widget.attrs['class'] = 'form-control is-invalid'

    def clean(self):
        cleaned_data = super().clean()
        nome = cleaned_data.get('nome')
        municipio = cleaned_data.get('municipio')
        contrato = self.contrato

        if contrato and nome and municipio:
            qs = Regional.objects.filter(contrato=contrato, nome=nome, municipio=municipio)
            # ✅ Ignora a própria instância no update
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                # Atrelar o erro geral (melhor UX)
                raise forms.ValidationError("Já existe uma regional com esse nome e município para este contrato.")

        return cleaned_data
