from django import forms
from .models import ContractConfiguration

class ContractConfigurationForm(forms.ModelForm):
    class Meta:
        model = ContractConfiguration
        fields = '__all__'