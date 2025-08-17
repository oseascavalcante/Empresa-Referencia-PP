from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import CustoDiretoFuncao, CustoDireto
from cad_contrato.models import CadastroContrato, Regional
from cadastro_equipe.models import Equipe, EscopoAtividade, FuncaoEquipe
from .services import EquipamentoCustoService
import json
import logging

logger = logging.getLogger('custo_direto')



class DashboardCustoDiretoView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Buscar todos os contratos que possuem dados de custos diretos OU composições de equipe
        contratos_com_custos = CustoDiretoFuncao.objects.values_list('contrato_id', flat=True).distinct()
        contratos_com_composicoes = CadastroContrato.objects.filter(
            equipes__composicaoequipe__isnull=False
        ).values_list('contrato', flat=True).distinct()
        
        # União de contratos com custos ou composições
        contratos_ids = list(set(list(contratos_com_custos) + list(contratos_com_composicoes)))
        
        if contratos_ids:
            contratos = CadastroContrato.objects.filter(contrato__in=contratos_ids)
        else:
            # Se não há contratos com dados, mostra todos
            contratos = CadastroContrato.objects.all()
        
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

        # Buscar equipes disponíveis baseado no contrato selecionado
        if contrato_id:
            # Primeiro tenta buscar equipes que já têm custos calculados
            equipes_com_custos = CustoDiretoFuncao.objects.filter(
                contrato_id=contrato_id
            ).values_list('composicao__equipe_id', flat=True).distinct()
            
            # Se não houver custos, busca equipes que têm composições
            if not equipes_com_custos:
                from cadastro_equipe.models import ComposicaoEquipe
                equipes_com_custos = ComposicaoEquipe.objects.filter(
                    contrato_id=contrato_id
                ).values_list('equipe_id', flat=True).distinct()
            
            equipes = Equipe.objects.filter(id__in=equipes_com_custos) if equipes_com_custos else Equipe.objects.none()
        else:
            equipes = Equipe.objects.filter(contrato__in=contratos_ids) if contratos_ids else Equipe.objects.none()

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

        # Calcular totais por categoria para mão de obra
        totais_mao_obra_categoria = {
            'SALARIO_PERICULOSIDADE': 0,
            'BENEFICIOS': 0,
            'ENCARGOS_SOCIAIS': 0,
            'HE_ADICIONAIS': 0,
            'OUTROS_CUSTOS': 0
        }
        
        # Calcular totais individuais para a linha de somatório
        totais_individuais_mao_obra = {
            'total_salario': 0,
            'total_beneficios': 0,
            'total_encargos': 0,
            'total_periculosidade': 0,
            'total_he50': 0,
            'total_he100': 0,
            'total_prontidao': 0,
            'total_sobreaviso': 0,
            'total_adicional': 0,
            'total_outros': 0,
            'total_geral': 0
        }
        
        # Agrupar custos por composição para gráfico de barras
        custos_mao_obra_por_composicao = {}
        for custo in custos_funcoes:
            # Agrupar por composição (contrato + equipe + regional + escopo)
            chave_composicao = f"{custo.contrato.contrato}_{custo.composicao.equipe.id}_{custo.composicao.regional.id}_{custo.composicao.escopo.id}"
            
            if chave_composicao not in custos_mao_obra_por_composicao:
                custos_mao_obra_por_composicao[chave_composicao] = {
                    'contrato': custo.contrato,
                    'equipe': custo.composicao.equipe,
                    'regional': custo.composicao.regional,
                    'escopo': custo.composicao.escopo,
                    'custos_categorias': {
                        'SALARIO_PERICULOSIDADE': 0,
                        'BENEFICIOS': 0,
                        'ENCARGOS_SOCIAIS': 0,
                        'HE_ADICIONAIS': 0,
                        'OUTROS_CUSTOS': 0
                    },
                    'custo_total': 0,
                    'quantidade_funcionarios': 0
                }
            
            # Calcular categorias agrupadas
            salario_periculosidade = custo.salario_base + custo.adicional_periculosidade
            beneficios = custo.beneficios
            encargos_sociais = custo.valor_total_encargos
            he_adicionais = (custo.valor_horas_extras_50 + custo.valor_horas_extras_100 + 
                           custo.valor_prontidao + custo.valor_sobreaviso + custo.valor_adicional_noturno)
            outros_custos = custo.outros_custos
            
            # Somar aos totais gerais
            totais_mao_obra_categoria['SALARIO_PERICULOSIDADE'] += salario_periculosidade
            totais_mao_obra_categoria['BENEFICIOS'] += beneficios
            totais_mao_obra_categoria['ENCARGOS_SOCIAIS'] += encargos_sociais
            totais_mao_obra_categoria['HE_ADICIONAIS'] += he_adicionais
            totais_mao_obra_categoria['OUTROS_CUSTOS'] += outros_custos
            
            # Somar aos totais individuais para linha de somatório
            totais_individuais_mao_obra['total_salario'] += custo.salario_base
            totais_individuais_mao_obra['total_beneficios'] += custo.beneficios
            totais_individuais_mao_obra['total_encargos'] += custo.valor_total_encargos
            totais_individuais_mao_obra['total_periculosidade'] += custo.adicional_periculosidade
            totais_individuais_mao_obra['total_he50'] += custo.valor_horas_extras_50
            totais_individuais_mao_obra['total_he100'] += custo.valor_horas_extras_100
            totais_individuais_mao_obra['total_prontidao'] += custo.valor_prontidao
            totais_individuais_mao_obra['total_sobreaviso'] += custo.valor_sobreaviso
            totais_individuais_mao_obra['total_adicional'] += custo.valor_adicional_noturno
            totais_individuais_mao_obra['total_outros'] += custo.outros_custos
            totais_individuais_mao_obra['total_geral'] += custo.custo_total
            
            # Somar aos totais por composição
            composicao = custos_mao_obra_por_composicao[chave_composicao]
            composicao['custos_categorias']['SALARIO_PERICULOSIDADE'] += salario_periculosidade
            composicao['custos_categorias']['BENEFICIOS'] += beneficios
            composicao['custos_categorias']['ENCARGOS_SOCIAIS'] += encargos_sociais
            composicao['custos_categorias']['HE_ADICIONAIS'] += he_adicionais
            composicao['custos_categorias']['OUTROS_CUSTOS'] += outros_custos
            composicao['custo_total'] += custo.custo_total
            composicao['quantidade_funcionarios'] += custo.quantidade_total_funcionarios

        # Dados do gráfico
        labels = []
        data = []
        for custo in custos_funcoes:
            label = f"{custo.funcao.nome} - {custo.composicao.equipe.nome} - {custo.contrato.contrato}"
            labels.append(label)
            data.append(float(custo.custo_por_funcionario))

        # Regionais e escopos disponíveis baseados no contrato selecionado
        if contrato_id:
            regionais = Regional.objects.filter(contrato_id=contrato_id)
            escopos = EscopoAtividade.objects.filter(contrato_id=contrato_id)
        else:
            # Se não há contrato específico, mostra regionais e escopos dos contratos com dados
            regionais = Regional.objects.filter(contrato_id__in=contratos_ids) if contratos_ids else Regional.objects.none()
            escopos = EscopoAtividade.objects.filter(contrato_id__in=contratos_ids) if contratos_ids else EscopoAtividade.objects.none()

        # Calcular custos de equipamentos
        custos_equipamentos = EquipamentoCustoService.calcular_custos_equipamentos_por_contrato(
            contrato_id=contrato_id,
            equipe_id=equipe_id,
            regional_id=regional_id,
            escopo_id=escopo_id
        )

        # Preparar dados dos equipamentos para JavaScript (convertendo Decimal para float)
        def decimal_to_float(obj):
            """Converte valores Decimal para float recursivamente"""
            if isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            elif hasattr(obj, '__dict__'):
                # Para objetos com atributos, converte os valores relevantes
                return obj
            else:
                from decimal import Decimal
                return float(obj) if isinstance(obj, Decimal) else obj

        # Converter totais por categoria para formato JavaScript seguro
        from decimal import Decimal
        totais_equipamentos_js = {}
        for categoria, valor in custos_equipamentos['totais_por_categoria'].items():
            totais_equipamentos_js[categoria] = float(valor) if isinstance(valor, Decimal) else valor
            
        # Converter custos por composição para formato JavaScript seguro
        custos_equipamentos_js = []
        for custo in custos_equipamentos['custos_por_composicao']:
            custos_categoria_js = {}
            for categoria, valor in custo['custos_categorias'].items():
                from decimal import Decimal
                custos_categoria_js[categoria] = float(valor) if isinstance(valor, Decimal) else valor
            
            custo_mensal = custo['custo_mensal_por_equipe']
            custo_mensal_float = float(custo_mensal) if isinstance(custo_mensal, Decimal) else custo_mensal
            
            quantidade_equipes = custo['quantidade_equipes']
            quantidade_equipes_int = int(quantidade_equipes) if isinstance(quantidade_equipes, Decimal) else quantidade_equipes
            
            custos_equipamentos_js.append({
                'equipe_nome': custo['equipe'].nome,
                'custo_mensal_por_equipe': custo_mensal_float,
                'quantidade_equipes': quantidade_equipes_int,
                'custos_categorias': custos_categoria_js
            })

        # Converter dados de mão de obra para formato JavaScript seguro
        totais_mao_obra_js = {}
        for categoria, valor in totais_mao_obra_categoria.items():
            totais_mao_obra_js[categoria] = float(valor) if isinstance(valor, Decimal) else valor
            
        # Converter custos por composição de mão de obra para formato JavaScript seguro
        custos_mao_obra_js = []
        for custo in custos_mao_obra_por_composicao.values():
            custos_categoria_js = {}
            for categoria, valor in custo['custos_categorias'].items():
                custos_categoria_js[categoria] = float(valor) if isinstance(valor, Decimal) else valor
            
            custo_total_float = float(custo['custo_total']) if isinstance(custo['custo_total'], Decimal) else custo['custo_total']
            quantidade_funcionarios_int = int(custo['quantidade_funcionarios']) if isinstance(custo['quantidade_funcionarios'], Decimal) else custo['quantidade_funcionarios']
            
            custos_mao_obra_js.append({
                'equipe_nome': custo['equipe'].nome,
                'custo_total': custo_total_float,
                'quantidade_funcionarios': quantidade_funcionarios_int,
                'custos_categorias': custos_categoria_js
            })

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
            
            # Dados dos equipamentos - formato original para templates
            'custos_equipamentos': custos_equipamentos['custos_por_composicao'],
            'totais_equipamentos_categoria': custos_equipamentos['totais_por_categoria'],
            'custo_total_equipamentos': custos_equipamentos['custo_total_geral'],
            'tem_dados_equipamentos': custos_equipamentos['tem_dados'],
            
            # Dados dos equipamentos - formato JavaScript seguro
            'totais_equipamentos_categoria_js': json.dumps(totais_equipamentos_js),
            'custos_equipamentos_js': json.dumps(custos_equipamentos_js),
            
            # Dados da mão de obra - formato original para templates
            'totais_mao_obra_categoria': totais_mao_obra_categoria,
            'totais_individuais_mao_obra': totais_individuais_mao_obra,
            'custos_mao_obra_por_composicao': list(custos_mao_obra_por_composicao.values()),
            'custo_total_mao_obra': sum(totais_mao_obra_categoria.values()),
            'tem_dados_mao_obra': len(custos_funcoes) > 0,
            
            # Dados da mão de obra - formato JavaScript seguro
            'totais_mao_obra_categoria_js': json.dumps(totais_mao_obra_js),
            'custos_mao_obra_js': json.dumps(custos_mao_obra_js),
        })

        return context


class RecalcularCustosView(View):
    """View para recalcular custos diretos via AJAX"""
    
    def post(self, request, *args, **kwargs):
        contrato_id = request.POST.get('contrato_id')
        
        try:
            if contrato_id:
                contrato = CadastroContrato.objects.get(contrato=contrato_id)
                funcoes_equipe = FuncaoEquipe.objects.filter(
                    contrato=contrato,
                    quantidade_funcionarios__gt=0
                )
            else:
                funcoes_equipe = FuncaoEquipe.objects.filter(quantidade_funcionarios__gt=0)
            
            if not funcoes_equipe.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Nenhuma função de equipe encontrada para processar.'
                })
            
            # Recalcula custos via signals (salvar novamente dispara o cálculo)
            sucessos = 0
            for funcao_equipe in funcoes_equipe:
                funcao_equipe.save()  # Dispara o signal
                sucessos += 1
            
            return JsonResponse({
                'success': True,
                'message': f'Custos recalculados com sucesso! {sucessos} funções processadas.'
            })
            
        except CadastroContrato.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Contrato não encontrado.'
            })
        except Exception as e:
            logger.error(f"Erro ao recalcular custos: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Erro ao recalcular custos: {str(e)}'
            })
