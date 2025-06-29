from django.views.generic import TemplateView
from .models import CustoDiretoFuncao, CustoDireto
from cad_contrato.models import CadastroContrato, Regional
from cadastro_equipe.models import Equipe, EscopoAtividade  # ✅ Import necessário
import json
import logging

logger = logging.getLogger('custo_direto')



class DashboardCustoDiretoView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        contratos_ids = CustoDireto.objects.values_list('contrato_id', flat=True)
        contratos = CadastroContrato.objects.filter(contrato__in=contratos_ids)
        
        # Filtros via GET
        contrato_id = self.request.GET.get('contrato')
        equipe_id = self.request.GET.get('equipe')
        regional_id = self.request.GET.get('regional')
        escopo_id = self.request.GET.get('escopo')

        # Base do queryset
        custos_funcoes_queryset = CustoDiretoFuncao.objects.select_related(
            'contrato', 'composicao', 'composicao__equipe', 'composicao__regional',
            'composicao__escopo', 'funcao'
        )

        if contrato_id:
            equipes_ids = CustoDiretoFuncao.objects.filter(contrato_id=contrato_id).values_list('composicao__equipe_id', flat=True).distinct()
            equipes = Equipe.objects.filter(id__in=equipes_ids)
        else:
            equipes = Equipe.objects.all()

        # Aplicar filtros
        if contrato_id:
            custos_funcoes_queryset = custos_funcoes_queryset.filter(contrato_id=contrato_id)
        if equipe_id:
            custos_funcoes_queryset = custos_funcoes_queryset.filter(composicao__equipe_id=equipe_id)
        if regional_id:
            custos_funcoes_queryset = custos_funcoes_queryset.filter(composicao__regional_id=regional_id)
        if escopo_id:
            custos_funcoes_queryset = custos_funcoes_queryset.filter(composicao__escopo_id=escopo_id)

        custos_funcoes_queryset = custos_funcoes_queryset.order_by('contrato')

        # Preparar dados para a tabela e gráfico
        custos_funcoes = []
        for custo in custos_funcoes_queryset:
            if custo.quantidade_total_funcionarios > 0:
                custo.custo_por_funcionario = custo.custo_total / custo.quantidade_total_funcionarios
            else:
                custo.custo_por_funcionario = 0
            custos_funcoes.append(custo)

        # Dados do gráfico
        labels = []
        data = []
        for custo in custos_funcoes:
            label = f"{custo.funcao.nome} - {custo.composicao.equipe.nome} - {custo.contrato.contrato}"
            labels.append(label)
            data.append(float(custo.custo_por_funcionario))

        # Regionais e escopos disponíveis
        regionais = Regional.objects.filter(contrato_id=contrato_id) if contrato_id else Regional.objects.none()
        escopos = EscopoAtividade.objects.all()

        # Atualiza contexto
        context.update({
            'grafico_labels': json.dumps(labels),
            'grafico_data': json.dumps(data),
            'custos_funcoes': custos_funcoes,
            'contratos': contratos,
            'equipes': equipes,
            'regionais': regionais,
            'escopos': escopos,
            'contrato_selecionado': str(contrato_id) if contrato_id else '',
            'equipe_selecionada': int(equipe_id) if equipe_id else '',
            'regional_selecionada': int(regional_id) if regional_id else '',
            'escopo_selecionado': int(escopo_id) if escopo_id else '',
        })

        return context

