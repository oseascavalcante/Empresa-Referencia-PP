from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from cad_contrato.models import CadastroContrato

def home(request):
    return render(request, "home.html")

def menu_cadastro_estrutura(request):
    contrato_id = request.session.get('contrato_id')
    if not contrato_id:
        return redirect(f"{reverse_lazy('selecionar_contrato')}?next={reverse_lazy('menu_cadastro_estrutura')}")
    contrato = CadastroContrato.objects.get(pk=contrato_id)
    return render(request, 'menu_cadastro_estrutura.html', {'contrato': contrato})