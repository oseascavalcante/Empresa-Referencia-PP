from django.views.generic import TemplateView
from .models import CustoDiretoFuncao
from cad_contrato.models import CadastroContrato

class DashboardCustoDiretoView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        contrato_id = self.request.GET.get('contrato')
        contratos = CadastroContrato.objects.all()

        if contrato_id:
            custos_funcoes = CustoDiretoFuncao.objects.select_related('contrato', 'funcao_equipe').filter(contrato_id=contrato_id)
        else:
            custos_funcoes = CustoDiretoFuncao.objects.select_related('contrato', 'funcao_equipe')

        context['custos_funcoes'] = custos_funcoes.order_by('contrato')
        context['contratos'] = contratos
        context['contrato_selecionado'] = contrato_id

        return context
