from django import forms
from .models import (
    Equipe,
    Funcao,
    ComposicaoEquipe,
    EscopoAtividade,
    FuncaoEquipe,
)


class FuncaoForm(forms.ModelForm):
    """Form para cadastro/edição de Função.

    - Recebe `contrato` via kwargs (ex.: view pega da sessão) e **não** expõe o campo no form.
    - Garante unicidade (contrato + nome) na validação de formulário.
    - Injeta o contrato em `save()` para remover redundância na view.
    """

    def __init__(self, *args, **kwargs):
        # Remove o kwarg extra antes do super, evitando TypeError do BaseModelForm
        self.contrato = kwargs.pop("contrato", None)
        super().__init__(*args, **kwargs)

        # Aparência dos widgets
        self.fields["nome"].widget.attrs.update({"class": "form-control"})
        self.fields["salario"].widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Funcao
        # Não expomos `contrato` — ele vem da sessão/kwargs
        fields = ["nome", "salario"]

    def clean(self):
        cleaned = super().clean()
        nome = cleaned.get("nome")
        if nome and self.contrato:
            qs = Funcao.objects.filter(contrato=self.contrato, nome=nome)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("nome", "Já existe uma função com este nome para este contrato.")
        return cleaned

    def save(self, commit: bool = True):
        # Garante o vínculo do contrato mesmo que a view não o defina explicitamente
        obj = super().save(commit=False)
        if self.contrato is not None:
            obj.contrato = self.contrato
        if commit:
            obj.save()
        return obj


class FuncaoEquipeForm(forms.ModelForm):
    """Form para funções dentro da composição de equipe.

    - Pode receber `contrato` para filtrar o queryset de `funcao` ao contexto correto.
    """

    def __init__(self, *args, **kwargs):
        contrato = kwargs.pop("contrato", None)
        super().__init__(*args, **kwargs)
        if contrato is not None:
            self.fields["funcao"].queryset = Funcao.objects.filter(contrato=contrato)

    class Meta:
        model = FuncaoEquipe
        fields = "__all__"


class EquipeForm(forms.ModelForm):
    """Form para Equipe.

    - Recebe `contrato` via kwargs.
    - Valida unicidade (contrato + nome).
    - Injeta o contrato em `save()` para evitar duplicar essa lógica na view.
    """

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop("contrato", None)
        super().__init__(*args, **kwargs)
        self.fields["nome"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Nome da equipe"
        })
        self.fields["descricao"].widget.attrs.update({
            "class": "form-control", 
            "placeholder": "Descrição da equipe"
        })
        
        # Adiciona classes de erro se existirem
        if self.errors:
            for field_name, field in self.fields.items():
                if field_name in self.errors:
                    if 'class' in field.widget.attrs:
                        field.widget.attrs['class'] += ' is-invalid'
                    else:
                        field.widget.attrs['class'] = 'form-control is-invalid'

    class Meta:
        model = Equipe
        fields = ["nome", "descricao"]

    def clean(self):
        cleaned = super().clean()
        nome = cleaned.get("nome")
        if nome and self.contrato:
            qs = Equipe.objects.filter(nome=nome, contrato=self.contrato)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error("nome", "Já existe uma equipe com este nome para este contrato.")
        return cleaned

    def save(self, commit: bool = True):
        obj = super().save(commit=False)
        if self.contrato is not None:
            obj.contrato = self.contrato
        if commit:
            obj.save()
        return obj


class EscopoAtividadeForm(forms.ModelForm):
    """
    - Recebe `contrato` via kwargs (não expõe no form).
    - Valida unicidade (contrato + nome) ignorando a própria instância no update.
    - Injeta o contrato no save().
    """
    class Meta:
        model = EscopoAtividade
        fields = ["nome", "descricao"]

    def __init__(self, *args, **kwargs):
        self.contrato = kwargs.pop('contrato', None)
        super().__init__(*args, **kwargs)
        # Aparência/UX consistente
        self.fields["nome"].widget.attrs.update({"class": "form-control"})
        self.fields["descricao"].widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned = super().clean()
        nome = cleaned.get("nome")
        if nome and self.contrato:
            qs = EscopoAtividade.objects.filter(contrato=self.contrato, nome__iexact=nome)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)  # ✅ ignora o próprio registro
            if qs.exists():
                self.add_error("nome", "Já existe um escopo com este nome para este contrato.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.contrato is not None:
            obj.contrato = self.contrato
        if commit:
            obj.save()
        return obj

class ComposicaoEquipeForm(forms.ModelForm):
    """Formulário para composição de equipe com integração de veículos."""

    def __init__(self, *args, **kwargs):
        # Remove o kwarg extra antes do super para evitar TypeError
        self.contrato = kwargs.pop("contrato", None)
        super().__init__(*args, **kwargs)
        
        # Filtrar veículos pelo contrato se fornecido
        if self.contrato:
            from veiculos.models import Veiculo
            self.fields["veiculo"].queryset = Veiculo.objects.filter(contrato=self.contrato)
        
        # Configurar widgets com classes CSS
        self.fields["veiculo"].widget.attrs.update({"class": "form-select"})
        self.fields["modalidade_veiculo"].widget.attrs.update({"class": "form-select"})
        self.fields["quantidade_veiculos"].widget.attrs.update({"class": "form-control", "step": "0.01", "min": "0"})
        self.fields["km_rodado"].widget.attrs.update({"class": "form-control", "step": "0.01", "min": "0"})

    class Meta:
        model = ComposicaoEquipe
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        contrato = cleaned_data.get("contrato")
        regional = cleaned_data.get("regional")
        escopo = cleaned_data.get("escopo")
        equipe = cleaned_data.get("equipe")
        
        # Validação de duplicidade (mantida)
        if contrato and regional and escopo and equipe:
            existe = ComposicaoEquipe.objects.filter(
                contrato=contrato,
                regional=regional,
                escopo=escopo,
                equipe=equipe,
            )
            if self.instance.pk:
                existe = existe.exclude(pk=self.instance.pk)
            if existe.exists():
                raise forms.ValidationError(
                    "Essa equipe já foi cadastrada para esta combinação de contrato, regional e escopo de atividade."
                )
        
        # Validações específicas de veículos
        veiculo = cleaned_data.get("veiculo")
        modalidade_veiculo = cleaned_data.get("modalidade_veiculo")
        quantidade_veiculos = cleaned_data.get("quantidade_veiculos", 0)
        
        # Se veículo selecionado, modalidade é obrigatória
        if veiculo and not modalidade_veiculo:
            self.add_error("modalidade_veiculo", "Modalidade é obrigatória quando veículo for selecionado.")
        
        # Se modalidade definida, veículo é obrigatório
        if modalidade_veiculo and not veiculo:
            self.add_error("veiculo", "Tipo de veículo é obrigatório quando modalidade for definida.")
        
        # Se quantidade > 0, veículo e modalidade são obrigatórios
        if quantidade_veiculos > 0:
            if not veiculo:
                self.add_error("veiculo", "Tipo de veículo é obrigatório quando quantidade for maior que zero.")
            if not modalidade_veiculo:
                self.add_error("modalidade_veiculo", "Modalidade é obrigatória quando quantidade for maior que zero.")
        
        return cleaned_data
