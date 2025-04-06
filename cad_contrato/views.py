from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import CadastroContrato
from .forms import CadastroContratoForm

class ContractCreateView(CreateView):
    model = CadastroContrato
    form_class = CadastroContratoForm
    template_name = 'cadastro_contrato.html'
    success_url = reverse_lazy('cadastro_contrato')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = CadastroContrato.objects.all()
        return context
    

def lista_formularios(request):
    # Simulando dados - substituir pela query real ao banco de dados
    dados = [
        {"tipo": "Upload", "variavel": "EPI - EPC", "data": "2024/11/28-14:28", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Upload", "variavel": "Equipes Mínimas", "data": "2024/12/02-16:39", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Indicadores macroeconômicos", "data": "2025/01/01-12:03", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Tempo Útil", "data": "2024/10/14-12:20", "usuario": "Usuário 2", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Salários", "data": "2025/01/01-12:32", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Veículos", "data": "2025/01/01-12:32", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Capital e investimento", "data": "2025/01/01-12:32", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Pessoal da Supervição e Administração", "data": "2025/01/01-12:32", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Encargos Sociais", "data": "2025/01/01-12:32", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
        {"tipo": "Formulário", "variavel": "Catálogo", "data": "2025/01/01-12:32", "usuario": "Usuário 1", "status": "✔", "acesso": "#"},
    ]

    return render(request, "lista_formularios.html", {"dados": dados})


def menu_principal(request):
    return render(request, "menu_principal.html")


def abrir_contratos(request):
    # Lógica para exibir a relação de contratos
    contracts = CadastroContrato.objects.all()  # Substitua pelo modelo correto
    return render(request, 'abrir_contratos.html', {'contracts': contracts})