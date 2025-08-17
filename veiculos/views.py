from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, View
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError
from django.contrib import messages
import json

from cad_contrato.models import CadastroContrato, Regional
from cadastro_equipe.models import EscopoAtividade
from .models import TipoVeiculo, Veiculo, PrecoCombustivel, AtribuicaoVeiculo
from .forms import TipoVeiculoForm, VeiculoForm, PrecoCombustivelForm, AtribuicaoVeiculoForm


# --------------------------------------------
# Helpers
# --------------------------------------------
def _get_contrato_from_session(request):
    """Helper para obter contrato da sessão."""
    contrato_id = request.session.get("contrato_id")
    return get_object_or_404(CadastroContrato, pk=contrato_id)


def _render_tabela_tipos_veiculos(request):
    """Renderiza tabela de tipos de veículos para HTMX."""
    from django.db.models import Count
    tipos = TipoVeiculo.objects.annotate(
        total_veiculos=Count('veiculos')
    ).order_by('categoria', 'nome')
    html = render_to_string(
        "veiculos/_lista_tipos_veiculos_inline.html",
        {"tipos": tipos},
        request=request,
    )
    return HttpResponse(html)


def _render_tabela_precos_combustivel(request, contrato):
    """Renderiza tabela de preços de combustível para HTMX."""
    precos = PrecoCombustivel.objects.filter(contrato=contrato).order_by('tipo_combustivel')
    html = render_to_string(
        "veiculos/_lista_precos_combustivel_inline.html",
        {"precos": precos, "contrato": contrato},
        request=request,
    )
    return HttpResponse(html)


def _render_tabela_veiculos(request, contrato):
    """Renderiza tabela de veículos para HTMX."""
    veiculos = Veiculo.objects.filter(contrato=contrato).order_by('tipo_veiculo__categoria', 'tipo_veiculo__nome')
    html = render_to_string(
        "veiculos/_lista_veiculos_inline.html",
        {"veiculos": veiculos, "contrato": contrato},
        request=request,
    )
    return HttpResponse(html)


def _render_tabela_atribuicoes(request, contrato):
    """Renderiza tabela de atribuições de veículos para HTMX."""
    atribuicoes = AtribuicaoVeiculo.objects.filter(contrato=contrato).order_by('regional', 'escopo', 'veiculo')
    html = render_to_string(
        "veiculos/_lista_atribuicoes_inline.html",
        {"atribuicoes": atribuicoes, "contrato": contrato},
        request=request,
    )
    return HttpResponse(html)


# --------------------------------------------
# CRUD Tipos de Veículos (Master Data)
# --------------------------------------------
class TipoVeiculoCreateView(CreateView):
    """View para cadastro de tipos de veículos (master data)."""
    model = TipoVeiculo
    form_class = TipoVeiculoForm
    template_name = "veiculos/cadastrar_tipo_veiculo.html"
    success_url = reverse_lazy("cadastrar_tipo_veiculo")

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") and request.GET.get("fragment") == "form":
            form = self.get_form()
            html = render_to_string(
                "veiculos/_form_tipo_veiculo_inline.html", 
                {"form": form}, 
                request=request
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_tipos_veiculos(self.request)
        return response

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            msg = "Erro no preenchimento do formulário."
            if form.errors.get("nome"):
                msg = form.errors["nome"][0]
            elif form.non_field_errors():
                msg = form.non_field_errors()[0]
            return JsonResponse({"error": msg}, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Incluir contagem de veículos por tipo
        from django.db.models import Count
        context["tipos"] = TipoVeiculo.objects.annotate(
            total_veiculos=Count('veiculos')
        ).order_by('categoria', 'nome')
        return context


class TipoVeiculoUpdateView(UpdateView):
    """View para edição de tipos de veículos."""
    model = TipoVeiculo
    form_class = TipoVeiculoForm
    template_name = "veiculos/editar_tipo_veiculo.html"
    success_url = reverse_lazy("cadastrar_tipo_veiculo")

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get("HX-Request") or request.GET.get("partial"):
            form = self.get_form()
            html = render_to_string(
                "veiculos/_form_editar_tipo_veiculo_inline.html",
                {"form": form, "obj": self.object},
                request=request
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_tipos_veiculos(self.request)
        return response

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "veiculos/_form_editar_tipo_veiculo_inline.html",
                {"form": form, "obj": self.object},
                request=self.request
            )
            return HttpResponse(html, status=400)
        return super().form_invalid(form)


class TipoVeiculoDeleteView(DeleteView):
    """View para exclusão de tipos de veículos."""
    model = TipoVeiculo
    success_url = reverse_lazy("cadastrar_tipo_veiculo")
    template_name = "veiculos/confirmar_excluir_tipo_veiculo.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            if request.headers.get("HX-Request"):
                return JsonResponse({
                    "error": "Este tipo de veículo está em uso e não pode ser excluído."
                }, status=409)
            messages.error(request, "Este tipo de veículo está em uso e não pode ser excluído.")
            return redirect(self.success_url)
        
        if request.headers.get("HX-Request"):
            return _render_tabela_tipos_veiculos(request)
        return redirect(self.success_url)


# --------------------------------------------
# CRUD Preços de Combustível
# --------------------------------------------
class PrecoCombustivelCreateView(CreateView):
    """View para configuração de preços de combustível por contrato."""
    model = PrecoCombustivel
    form_class = PrecoCombustivelForm
    template_name = "veiculos/configurar_precos_combustivel.html"
    success_url = reverse_lazy("configurar_precos_combustivel")

    def dispatch(self, request, *args, **kwargs):
        contrato_id = self.kwargs.get('contrato_id') or request.session.get('contrato_id')
        if not contrato_id:
            return redirect('selecionar_contrato')
        self.contrato = get_object_or_404(CadastroContrato, pk=contrato_id)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["contrato"] = self.contrato
        return kwargs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") and request.GET.get("fragment") == "form":
            form = self.get_form()
            html = render_to_string(
                "veiculos/_form_preco_combustivel_inline.html",
                {"form": form, "contrato": self.contrato},
                request=request
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.contrato = self.contrato
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_precos_combustivel(self.request, self.contrato)
        return response

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            msg = "Erro no preenchimento do formulário."
            if form.errors.get("tipo_combustivel"):
                msg = form.errors["tipo_combustivel"][0]
            elif form.non_field_errors():
                msg = form.non_field_errors()[0]
            return JsonResponse({"error": msg}, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contrato"] = self.contrato
        
        # Inicializar automaticamente preços para todos os tipos de combustível
        self._inicializar_tipos_combustivel()
        
        context["precos"] = PrecoCombustivel.objects.filter(
            contrato=self.contrato
        ).order_by('tipo_combustivel')
        return context
    
    def _inicializar_tipos_combustivel(self):
        """Cria entradas automáticas para tipos de combustível que ainda não existem."""
        tipos_existentes = PrecoCombustivel.objects.filter(
            contrato=self.contrato
        ).values_list('tipo_combustivel', flat=True)
        
        todos_tipos = [choice[0] for choice in PrecoCombustivel.TIPO_COMBUSTIVEL_CHOICES]
        
        for tipo in todos_tipos:
            if tipo not in tipos_existentes:
                PrecoCombustivel.objects.create(
                    contrato=self.contrato,
                    tipo_combustivel=tipo,
                    preco_por_litro=0.000
                )

    def get_success_url(self):
        return reverse_lazy('configurar_precos_combustivel', kwargs={'contrato_id': self.contrato.pk})


class PrecoCombustivelUpdateView(UpdateView):
    """View para edição de preços de combustível."""
    model = PrecoCombustivel
    form_class = PrecoCombustivelForm
    template_name = "veiculos/editar_preco_combustivel.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.contrato_id:
            kwargs["contrato"] = self.object.contrato
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get("HX-Request") or request.GET.get("partial"):
            form = self.get_form()
            html = render_to_string(
                "veiculos/_form_editar_preco_combustivel_inline.html",
                {"form": form, "obj": self.object, "contrato": self.object.contrato},
                request=request
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_precos_combustivel(self.request, self.object.contrato)
        return response

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "veiculos/_form_editar_preco_combustivel_inline.html",
                {"form": form, "obj": self.object, "contrato": self.object.contrato},
                request=self.request
            )
            return HttpResponse(html, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('configurar_precos_combustivel', kwargs={'contrato_id': self.object.contrato.pk})


class PrecoCombustivelDeleteView(DeleteView):
    """View para exclusão de preços de combustível."""
    model = PrecoCombustivel
    template_name = "veiculos/confirmar_excluir_preco_combustivel.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        contrato = self.object.contrato
        try:
            # Ao invés de deletar, resetar preço para zero
            self.object.preco_por_litro = 0.000
            self.object.save()
        except Exception as e:
            if request.headers.get("HX-Request"):
                return JsonResponse({
                    "error": f"Erro ao resetar preço: {str(e)}"
                }, status=409)
            messages.error(request, f"Erro ao resetar preço: {str(e)}")
            return redirect(self.get_success_url())
        
        if request.headers.get("HX-Request"):
            return _render_tabela_precos_combustivel(request, contrato)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('configurar_precos_combustivel', kwargs={'contrato_id': self.object.contrato.pk})


# --------------------------------------------
# CRUD Veículos
# --------------------------------------------
class VeiculoCreateView(CreateView):
    """View para cadastro de veículos por contrato."""
    model = Veiculo
    form_class = VeiculoForm
    template_name = "veiculos/cadastrar_veiculo.html"
    success_url = reverse_lazy("cadastrar_veiculo")

    def dispatch(self, request, *args, **kwargs):
        contrato_id = self.kwargs.get('contrato_id') or request.session.get('contrato_id')
        if not contrato_id:
            return redirect('selecionar_contrato')
        self.contrato = get_object_or_404(CadastroContrato, pk=contrato_id)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["contrato"] = self.contrato
        return kwargs

    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") and request.GET.get("fragment") == "form":
            form = self.get_form()
            html = render_to_string(
                "veiculos/_form_veiculo_inline.html",
                {"form": form, "contrato": self.contrato},
                request=request
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.contrato = self.contrato
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_veiculos(self.request, self.contrato)
        return response

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            msg = "Erro no preenchimento do formulário."
            if form.errors.get("tipo_veiculo"):
                msg = form.errors["tipo_veiculo"][0]
            elif form.non_field_errors():
                msg = form.non_field_errors()[0]
            return JsonResponse({"error": msg}, status=400)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contrato"] = self.contrato
        context["veiculos"] = Veiculo.objects.filter(
            contrato=self.contrato
        ).select_related('tipo_veiculo').order_by('tipo_veiculo__categoria', 'tipo_veiculo__nome')
        return context

    def get_success_url(self):
        return reverse_lazy('cadastrar_veiculo', kwargs={'contrato_id': self.contrato.pk})


class VeiculoUpdateView(UpdateView):
    """View para edição de veículos."""
    model = Veiculo
    form_class = VeiculoForm
    template_name = "veiculos/editar_veiculo.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.object and self.object.contrato_id:
            kwargs["contrato"] = self.object.contrato
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get("HX-Request") or request.GET.get("partial"):
            form = self.get_form()
            html = render_to_string(
                "veiculos/_form_editar_veiculo_inline.html",
                {"form": form, "obj": self.object, "contrato": self.object.contrato},
                request=request
            )
            return HttpResponse(html)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get("HX-Request"):
            return _render_tabela_veiculos(self.request, self.object.contrato)
        return response

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "veiculos/_form_editar_veiculo_inline.html",
                {"form": form, "obj": self.object, "contrato": self.object.contrato},
                request=self.request
            )
            return HttpResponse(html, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('cadastrar_veiculo', kwargs={'contrato_id': self.object.contrato.pk})


class VeiculoDeleteView(DeleteView):
    """View para exclusão de veículos."""
    model = Veiculo
    template_name = "veiculos/confirmar_excluir_veiculo.html"

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            contrato = self.object.contrato
            
            # Tentar excluir o veículo
            self.object.delete()
            
            if request.headers.get("HX-Request"):
                return _render_tabela_veiculos(request, contrato)
            return redirect(self.get_success_url())
            
        except ProtectedError:
            if request.headers.get("HX-Request"):
                return JsonResponse({
                    "error": "Este veículo está em uso e não pode ser excluído."
                }, status=409)
            messages.error(request, "Este veículo está em uso e não pode ser excluído.")
            return redirect(self.get_success_url())
            
        except Exception as e:
            if request.headers.get("HX-Request"):
                return JsonResponse({
                    "error": f"Erro ao excluir veículo: {str(e)}"
                }, status=500)
            messages.error(request, f"Erro ao excluir veículo: {str(e)}")
            return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('cadastrar_veiculo', kwargs={'contrato_id': self.object.contrato.pk})


# --------------------------------------------
# View de Atribuição de Veículos
# --------------------------------------------
class AtribuicaoVeiculoView(View):
    """View para atribuição de veículos a regionais e escopos."""
    template_name = "veiculos/atribuir_veiculos.html"

    def dispatch(self, request, *args, **kwargs):
        contrato_id = self.kwargs.get('contrato_id') or request.session.get('contrato_id')
        if not contrato_id:
            return redirect('selecionar_contrato')
        self.contrato = get_object_or_404(CadastroContrato, pk=contrato_id)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Handle JSON data requests
        if kwargs.get('atribuicao_id') and request.resolver_match.url_name == 'atribuicao_json':
            return self.post(request, *args, **kwargs)
        
        # Normal GET request
        context = {
            'contrato': self.contrato,
            'atribuicoes': AtribuicaoVeiculo.objects.filter(
                contrato=self.contrato
            ).select_related('regional', 'escopo', 'veiculo', 'veiculo__tipo_veiculo').order_by('regional', 'escopo', 'veiculo'),
            'regionais': Regional.objects.filter(contrato=self.contrato).order_by('nome'),
            'escopos': EscopoAtividade.objects.filter(contrato=self.contrato).order_by('nome'),
            'veiculos': Veiculo.objects.filter(contrato=self.contrato).select_related('tipo_veiculo').order_by('tipo_veiculo__categoria', 'tipo_veiculo__nome'),
            'form': AtribuicaoVeiculoForm(contrato=self.contrato)
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Salvar atribuição via AJAX."""
        try:
            # Check if it's an edit or delete operation
            atribuicao_id = kwargs.get('atribuicao_id')
            url_name = request.resolver_match.url_name
            
            if url_name == 'atribuicao_json':
                # Return JSON data for editing
                atribuicao = get_object_or_404(AtribuicaoVeiculo, pk=atribuicao_id, contrato=self.contrato)
                return JsonResponse({
                    'regional_id': atribuicao.regional.pk,
                    'escopo_id': atribuicao.escopo.pk,
                    'veiculo_id': atribuicao.veiculo.pk,
                    'quantidade': float(atribuicao.quantidade),
                    'observacoes': atribuicao.observacoes or ''
                })
            
            elif url_name == 'editar_atribuicao':
                # Update existing attribution
                atribuicao = get_object_or_404(AtribuicaoVeiculo, pk=atribuicao_id, contrato=self.contrato)
                data = json.loads(request.body)
                
                atribuicao.regional_id = data.get('regional_id')
                atribuicao.escopo_id = data.get('escopo_id')
                atribuicao.veiculo_id = data.get('veiculo_id')
                atribuicao.quantidade = data.get('quantidade')
                atribuicao.observacoes = data.get('observacoes', '')
                atribuicao.save()
                
                return JsonResponse({"success": True})
            
            else:
                # Create new attribution
                data = json.loads(request.body)
                form = AtribuicaoVeiculoForm(data, contrato=self.contrato)
                
                if form.is_valid():
                    form.save()
                    return JsonResponse({"success": True})
                else:
                    return JsonResponse({"success": False, "errors": form.errors}, status=400)
                
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    def delete(self, request, *args, **kwargs):
        """Excluir atribuição via AJAX."""
        try:
            atribuicao_id = kwargs.get('atribuicao_id')
            atribuicao = get_object_or_404(AtribuicaoVeiculo, pk=atribuicao_id, contrato=self.contrato)
            atribuicao.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
