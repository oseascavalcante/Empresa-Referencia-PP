from django import forms
from .models import Equipe, Funcao, ComposicaoEquipe, EscopoAtividade

class FuncaoForm(forms.ModelForm):
    class Meta:
        model = Funcao
        fields = '__all__'


class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EscopoAtividadeForm(forms.ModelForm):
    class Meta:
        model = EscopoAtividade
        fields = ['nome', 'descricao']  # Campos disponíveis no formulário        from django import forms
        from .models import EscopoAtividade
        
        class EscopoAtividadeForm(forms.ModelForm):
            class Meta:
                model = EscopoAtividade
                fields = ['nome', 'descricao']  # Campos disponíveis no formulário


class ComposicaoEquipeForm(forms.ModelForm):
    class Meta:
        model = ComposicaoEquipe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        contrato = cleaned_data.get("contrato")
        regional = cleaned_data.get("regional")
        escopo = cleaned_data.get("escopo")
        equipe = cleaned_data.get("equipe")

        if contrato and regional and escopo and equipe:
            existe = ComposicaoEquipe.objects.filter(
                contrato=contrato,
                regional=regional,
                escopo=escopo,
                equipe=equipe
            )

            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)

            if existe.exists():
                raise forms.ValidationError("Essa equipe já foi cadastrada para esta combinação de contrato, regional e escopo de atividade.")

        return cleaned_data

