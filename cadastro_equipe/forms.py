from django import forms
from .models import Equipe, Funcao, ComposicaoEquipe

class FuncaoForm(forms.ModelForm):
    class Meta:
        model = Funcao
        fields = '__all__'


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = '__all__'


class ComposicaoEquipeForm(forms.ModelForm):
    class Meta:
        model = ComposicaoEquipe
        fields = '__all__'
        widgets = {
            'periculosidade': forms.CheckboxInput(),
        }
