from django.views.generic import TemplateView
from .models import CustoDiretoFuncao, CustoDireto
from cad_contrato.models import CadastroContrato
from cadastro_equipe.models import Equipe  # ✅ Import necessário
import json
import logging

logger = logging.getLogger('custo_direto')


class DashboardCustoDiretoView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        contratos_ids = CustoDireto.objects.values_list('contrato_id', flat=True)
        contratos = CadastroContrato.objects.filter(contrato__in=contratos_ids)
        equipes = Equipe.objects.all()

        contrato_id = self.request.GET.get('contrato')
        equipe_id = self.request.GET.get('equipe')

        custos_funcoes = CustoDiretoFuncao.objects.select_related(
            'contrato', 'composicao', 'composicao__equipe', 'funcao'
        )

        if contrato_id:
            custos_funcoes = custos_funcoes.filter(contrato_id=contrato_id)

        if equipe_id:
            custos_funcoes = custos_funcoes.filter(composicao__equipe_id=equipe_id)

        custos_funcoes = custos_funcoes.order_by('contrato')

        # Gráfico
        labels = []
        data = []

        for custo in custos_funcoes:
            label = f"{custo.funcao.nome} - {custo.composicao.equipe.nome} - {custo.contrato.contrato}"
            labels.append(label)
            data.append(float(custo.custo_total))

        context.update({
            'grafico_labels': json.dumps(labels),
            'grafico_data': json.dumps(data),
            'custos_funcoes': custos_funcoes,
            'contratos': contratos,
            'equipes': equipes,
            'contrato_selecionado': contrato_id,
            'equipe_selecionada': int(equipe_id) if equipe_id else '',
        })

        return context
