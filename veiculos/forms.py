from django import forms
from .models import TipoVeiculo, Veiculo, PrecoCombustivel, AtribuicaoVeiculo
from cad_contrato.models import Regional
from cadastro_equipe.models import EscopoAtividade


class TipoVeiculoForm(forms.ModelForm):
    """
    Formulário para cadastro de tipos de veículos (master data).
    Não parametrizado por contrato.
    """
    class Meta:
        model = TipoVeiculo
        fields = ['nome', 'categoria', 'descricao', 'especificacoes_tecnicas']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Caminhonete S10'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do tipo de veículo...'
            }),
            'especificacoes_tecnicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Especificações técnicas detalhadas...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs['autofocus'] = True


class PrecoCombustivelForm(forms.ModelForm):
    """
    Formulário para configuração de preços de combustível por contrato.
    """
    class Meta:
        model = PrecoCombustivel
        fields = ['tipo_combustivel', 'preco_por_litro']
        widgets = {
            'tipo_combustivel': forms.Select(attrs={
                'class': 'form-select'
            }),
            'preco_por_litro': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0',
                'placeholder': 'Ex: 5.879'
            }),
        }

    def __init__(self, *args, contrato=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.contrato = contrato
        if contrato:
            # Filtrar tipos com preço zero (ainda não configurados) para mostrar apenas os disponíveis
            tipos_com_preco = PrecoCombustivel.objects.filter(
                contrato=contrato,
                preco_por_litro__gt=0
            ).values_list('tipo_combustivel', flat=True)
            
            if self.instance.pk:
                # Se estamos editando, inclui o tipo atual
                tipos_com_preco = tipos_com_preco.exclude(pk=self.instance.pk)
            
            choices = [choice for choice in PrecoCombustivel.TIPO_COMBUSTIVEL_CHOICES 
                      if choice[0] not in tipos_com_preco]
            
            if not choices and not self.instance.pk:
                self.fields['tipo_combustivel'].widget.attrs['disabled'] = True
                self.fields['tipo_combustivel'].help_text = "Todos os tipos de combustível já foram configurados."
            else:
                self.fields['tipo_combustivel'].choices = [('', 'Selecione...')] + choices

    def save(self, commit=True):
        # Se não temos uma instância e existe um preço para este tipo, atualizar em vez de criar
        if not self.instance.pk and self.contrato:
            tipo_combustivel = self.cleaned_data.get('tipo_combustivel')
            if tipo_combustivel:
                try:
                    existing = PrecoCombustivel.objects.get(
                        contrato=self.contrato,
                        tipo_combustivel=tipo_combustivel
                    )
                    # Atualizar entrada existente
                    existing.preco_por_litro = self.cleaned_data.get('preco_por_litro')
                    if commit:
                        existing.save()
                    return existing
                except PrecoCombustivel.DoesNotExist:
                    pass
        
        instance = super().save(commit=False)
        if self.contrato:
            instance.contrato = self.contrato
        if commit:
            instance.save()
        return instance


class VeiculoForm(forms.ModelForm):
    """
    Formulário para cadastro de veículos parametrizado por contrato.
    """
    class Meta:
        model = Veiculo
        fields = [
            'tipo_veiculo', 'valor_aquisicao', 'valor_locacao', 'vida_util_meses',
            'custo_mensal_seguro', 'custo_mensal_manutencao',
            'tipo_combustivel', 'eficiencia_km_litro',
            'observacoes'
        ]
        widgets = {
            'tipo_veiculo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valor_aquisicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ex: 50000.00'
            }),
            'valor_locacao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ex: 1500.00'
            }),
            'vida_util_meses': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Ex: 60 (5 anos)'
            }),
            'custo_mensal_seguro': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ex: 300.00'
            }),
            'custo_mensal_manutencao': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ex: 500.00'
            }),
            'tipo_combustivel': forms.Select(attrs={
                'class': 'form-select'
            }),
            'eficiencia_km_litro': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Ex: 12.50'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações sobre o veículo...'
            }),
        }

    def __init__(self, *args, contrato=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.contrato = contrato
        
        if contrato:
            # Filtrar tipos de veículos já cadastrados para este contrato
            tipos_existentes = Veiculo.objects.filter(
                contrato=contrato
            ).values_list('tipo_veiculo', flat=True)
            
            if self.instance.pk:
                # Se estamos editando, inclui o tipo atual
                tipos_existentes = tipos_existentes.exclude(pk=self.instance.pk)
            
            self.fields['tipo_veiculo'].queryset = TipoVeiculo.objects.exclude(
                id__in=tipos_existentes
            ).order_by('categoria', 'nome')
            
            if not self.fields['tipo_veiculo'].queryset.exists() and not self.instance.pk:
                self.fields['tipo_veiculo'].widget.attrs['disabled'] = True
                self.fields['tipo_veiculo'].help_text = "Todos os tipos disponíveis já foram cadastrados."

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.contrato:
            instance.contrato = self.contrato
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        tipo_combustivel = cleaned_data.get('tipo_combustivel')
        
        # Validar se existe preço cadastrado para o tipo de combustível
        if tipo_combustivel and self.contrato:
            if not PrecoCombustivel.objects.filter(
                contrato=self.contrato,
                tipo_combustivel=tipo_combustivel
            ).exists():
                self.add_error('tipo_combustivel', 
                             f'Preço não configurado para {dict(Veiculo.TIPO_COMBUSTIVEL_CHOICES)[tipo_combustivel]}. '
                             'Configure o preço antes de cadastrar o veículo.')
        
        return cleaned_data


class AtribuicaoVeiculoForm(forms.ModelForm):
    """
    Formulário para atribuição de veículos a regionais e escopos.
    """
    class Meta:
        model = AtribuicaoVeiculo
        fields = ['veiculo', 'regional', 'escopo', 'quantidade', 'observacoes']
        widgets = {
            'veiculo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'regional': forms.Select(attrs={
                'class': 'form-select'
            }),
            'escopo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Ex: 2.00'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações sobre a atribuição...'
            }),
        }

    def __init__(self, *args, contrato=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.contrato = contrato
        
        if contrato:
            # Filtrar dados relacionados ao contrato
            self.fields['veiculo'].queryset = Veiculo.objects.filter(
                contrato=contrato
            ).order_by('tipo_veiculo__categoria', 'tipo_veiculo__nome')
            
            self.fields['regional'].queryset = Regional.objects.filter(
                contrato=contrato
            ).order_by('nome')
            
            self.fields['escopo'].queryset = EscopoAtividade.objects.filter(
                contrato=contrato
            ).order_by('nome')
            
            # Verificar se existem dados suficientes
            if not self.fields['veiculo'].queryset.exists():
                for field_name in ['veiculo', 'regional', 'escopo', 'quantidade']:
                    self.fields[field_name].widget.attrs['disabled'] = True
                self.fields['veiculo'].help_text = "Cadastre veículos antes de fazer atribuições."
                
            elif not self.fields['regional'].queryset.exists():
                for field_name in ['regional', 'escopo', 'quantidade']:
                    self.fields[field_name].widget.attrs['disabled'] = True
                self.fields['regional'].help_text = "Cadastre regionais antes de fazer atribuições."
                
            elif not self.fields['escopo'].queryset.exists():
                for field_name in ['escopo', 'quantidade']:
                    self.fields[field_name].widget.attrs['disabled'] = True
                self.fields['escopo'].help_text = "Cadastre escopos antes de fazer atribuições."

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.contrato:
            instance.contrato = self.contrato
        if commit:
            instance.save()
        return instance