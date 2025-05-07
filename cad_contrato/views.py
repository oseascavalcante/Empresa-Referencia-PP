from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView, DetailView, UpdateView
from .models import CadastroContrato
from .forms import CadastroContratoForm
from django import forms

class ContractCreateView(CreateView):
    model = CadastroContrato
    form_class = CadastroContratoForm
    template_name = 'cadastro_contrato.html'
    success_url = reverse_lazy('home')  # Redireciona para a página inicial após o cadastro

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


class SelecionarContratoForm(forms.Form):
    contrato_id = forms.ModelChoiceField(
        queryset=CadastroContrato.objects.all(),
        label="Contrato",
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Selecione um contrato"
    )


class SelecionarContratoView(FormView):
    template_name = "selecionar_contrato.html"
    form_class = SelecionarContratoForm

    def form_valid(self, form):
        contrato = form.cleaned_data["contrato_id"]
        self.request.session["contrato_id"] = contrato.contrato

        next_url = self.request.GET.get("next") or "/"
        return redirect(next_url)
    

class MenuDespesasView(TemplateView):
    template_name = 'menu_despesas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato_id = self.kwargs.get('contrato_id')  # Obtém o ID do contrato da URL
        contrato = CadastroContrato.objects.filter(contrato=contrato_id).first()  # Busca o contrato no banco de dados

        if contrato:
            context['contrato'] = contrato
            context['total_geral'] = contrato.valor_inicial  # Exemplo: usa o valor inicial do contrato
        else:
            context['contrato'] = None
            context['total_geral'] = 0.00  # Valor padrão caso o contrato não seja encontrado

        return context


class DetailContratosView(DetailView):
    model = CadastroContrato
    template_name = 'detalhes_contrato.html'
    context_object_name = 'contrato'

    def get_object(self, queryset=None):
        contrato_id = self.kwargs.get('pk')  # 'pk' é o padrão usado pelo DetailView
        return CadastroContrato.objects.get(contrato=contrato_id)
    

class UpdateContratoView(UpdateView):
    model = CadastroContrato
    template_name = 'cadastro_contrato.html'
    fields = [
        'concessionaria', 'estado', 'municipio', 'escopo_contrato',
        'inicio_vigencia_contrato', 'fim_vigencia_contrato',
        'status_contrato', 'valor_inicial', 'descricao_alteracao', 'versao_base', 'numero_versao',
    ]
    context_object_name = 'contrato'

    def get_success_url(self):
        # Redireciona para o template `menu_despesas` após o update
        return reverse_lazy('menu_despesas', kwargs={'contrato_id': self.object.contrato})