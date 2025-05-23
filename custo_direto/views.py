import logging
import json
from django.views.generic import TemplateView
from .models import CustoDiretoFuncao, CustoDireto
from cad_contrato.models import CadastroContrato

logger = logging.getLogger('custo_direto')

class DashboardCustoDiretoView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filtra contratos que possuem custo direto
        contratos_ids = CustoDireto.objects.values_list('contrato_id', flat=True)
        contratos = CadastroContrato.objects.filter(contrato__in=contratos_ids)

        contrato_id = self.request.GET.get('contrato')

        custos_funcoes = CustoDiretoFuncao.objects.select_related(
            'contrato', 'composicao', 'composicao__equipe', 'funcao'
        )

        if contrato_id:
            custos_funcoes = custos_funcoes.filter(contrato_id=contrato_id)

        custos_funcoes = custos_funcoes.order_by('contrato')

        # Log dos custos
        logger.info("🚀 Custos Diretos Encontrados:")
        for custo in custos_funcoes:
            logger.info(
                f"Contrato: {custo.contrato.contrato} | Equipe: {custo.composicao.equipe.nome} | "
                f"Função: {custo.funcao.nome} | Custo Total: {custo.custo_total}"
            )

        # Dados para o gráfico
        labels = []
        data = []

        for custo in custos_funcoes:
            label = f"{custo.funcao.nome} - {custo.composicao.equipe.nome} - {custo.contrato.contrato}"
            labels.append(label)
            data.append(float(custo.custo_total))  # Garante que é numérico

        context['grafico_labels'] = json.dumps(labels)
        context['grafico_data'] = json.dumps(data)

        context['custos_funcoes'] = custos_funcoes
        context['contratos'] = contratos
        context['contrato_selecionado'] = contrato_id

        return context
