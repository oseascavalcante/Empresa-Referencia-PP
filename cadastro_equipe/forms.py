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
        fields = ['equipe', 'quantidade_equipes', 'data_mobilizacao', 'data_desmobilizacao', 'observacao']

    def __init__(self, *args, **kwargs):
        contrato = kwargs.pop('contrato', None)  # Recebe o contrato como argumento
        super().__init__(*args, **kwargs)

        if contrato:
            # Filtra as equipes que ainda não foram cadastradas para o contrato
            equipes_cadastradas = ComposicaoEquipe.objects.filter(contrato=contrato).values_list('equipe_id', flat=True)
            self.fields['equipe'].queryset = Equipe.objects.exclude(id__in=equipes_cadastradas)