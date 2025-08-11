from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, TemplateView, DetailView, UpdateView
from django.views.generic.edit import DeleteView

from mao_obra.services import GrupoCalculationsService
from .models import CadastroContrato, Regional
from .forms import CadastroContratoForm, RegionalForm
from django import forms

from .services import CadastroContratoService  # ✅ importa a service

from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models.deletion import ProtectedError

class ContractCreateView(CreateView):
    model = CadastroContrato
    form_class = CadastroContratoForm
    template_name = 'cadastro_contrato.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contracts'] = CadastroContrato.objects.all()
        return context

    def form_valid(self, form):
        # Primeiro salva o contrato no banco
        response = super().form_valid(form)

        CadastroContratoService.inicializar_contrato(self.object)
        GrupoCalculationsService.calcular_todos_grupos(self.object.pk)

        # Retorna normalmente
        return response



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

class SelecionarContratoView(View):
    def get(self, request):
        contratos = CadastroContrato.objects.all()
        return render(request, "selecionar_contrato.html", {"contratos": contratos})

    def post(self, request):
        contrato_id = request.POST.get("contrato_id")
        next_url = request.GET.get("next") or reverse_lazy("menu_cadastro_estrutura")
        if contrato_id:
            request.session["contrato_id"] = contrato_id
            return redirect(next_url)
        contratos = CadastroContrato.objects.all()
        return render(request, "selecionar_contrato.html", {
            "contratos": contratos,
            "erro": "Selecione um contrato.",
        })
        
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
    

class RegionalCreateView(CreateView):
    model = Regional
    form_class = RegionalForm
    template_name = 'adicionar_regional.html'

    def dispatch(self, request, *args, **kwargs):
        contrato_id = self.kwargs.get('contrato_id') or request.session.get('contrato_id')
        if not contrato_id:
            return redirect('selecionar_contrato')  # força usuário a selecionar um contrato

        self.contrato = get_object_or_404(CadastroContrato, pk=contrato_id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.contrato = self.contrato  # contrato já definido no dispatch
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_regionais(self.request, self.contrato)
        return response

    def get_initial(self):
        return {'contrato': self.contrato}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contrato'] = self.contrato
        context['regionais'] = Regional.objects.filter(contrato=self.contrato)
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['contrato'] = self.contrato  # passa o contrato para o form
        return kwargs

    def get_success_url(self):
        return reverse_lazy('adicionar_regional', kwargs={'contrato_id': self.object.contrato.pk if hasattr(self.object.contrato, "pk") else self.object.contrato})

    def get(self, request, *args, **kwargs):
        if request.GET.get("fragment") == "form":
            form = RegionalForm(contrato=self.contrato)
            html = render_to_string("_form_adicionar_regional_inline.html", {"form": form, "contrato": self.contrato}, request=request)
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)    

def _render_tabela_regionais(request, contrato):
    regionais = Regional.objects.filter(contrato=contrato).order_by("nome")
    html = render_to_string("_lista_regionais_inline.html", {"regionais": regionais, "contrato": contrato}, request=request)
    return HttpResponse(html)

class RegionalUpdateView(UpdateView):
    model = Regional
    form_class = RegionalForm
    template_name = "editar_regional.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.contrato_id:
            kwargs["contrato"] = self.object.contrato
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get("HX-Request") or request.GET.get("partial"):
            form = self.get_form()
            html = render_to_string("_form_editar_regional_inline.html", {"form": form, "obj": self.object, "contrato": self.object.contrato}, request=request)
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string("_form_editar_regional_inline.html",
                                    {"form": form, "obj": self.object, "contrato": self.object.contrato},
                                    request=self.request)
            resp = HttpResponse(html, status=400)
            resp['HX-Retarget'] = '#regional-form'
            return resp
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.contrato = self.object.contrato
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            # Retorna apenas a tabela para atualizar #lista-regionais
            html = render_to_string("_lista_regionais_inline.html", {
                "regionais": Regional.objects.filter(contrato=self.object.contrato),
                "contrato": self.object.contrato
            }, request=self.request)
            resp = HttpResponse(html)
            resp['HX-Retarget'] = '#lista-regionais'
            return resp
        return response

    def get_success_url(self):
        return reverse_lazy('adicionar_regional', kwargs={'contrato_id': self.object.contrato.pk})
    
class RegionalDeleteView(DeleteView):
    model = Regional
    template_name = "confirmar_excluir_regional.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        contrato = self.object.contrato
        try:
            self.object.delete()
        except ProtectedError:
            if request.headers.get("HX-Request"):
                return JsonResponse({"error": "Esta regional está em uso e não pode ser excluída."}, status=409)
            from django.contrib import messages
            messages.error(request, "Esta regional está em uso e não pode ser excluída.")
            return redirect(self.success_url)
        if request.headers.get("HX-Request"):
            return _render_tabela_regionais(request, contrato)
        return redirect(self.success_url)

    @property
    def success_url(self):
        return reverse_lazy('adicionar_regional', kwargs={'contrato_id': self.object.contrato.pk})