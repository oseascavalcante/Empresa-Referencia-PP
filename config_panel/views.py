from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import ContractConfiguration
from .forms import ContractConfigurationForm

class ContractCreateView(CreateView):
    model = ContractConfiguration
    form_class = ContractConfigurationForm
    template_name = 'contract_form.html'
    success_url = reverse_lazy('contract_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = ContractConfiguration.objects.all()
        return context