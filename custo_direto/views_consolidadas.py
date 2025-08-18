from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from cad_contrato.models import CadastroContrato
from .models import ConsolidacaoCustoContrato, CustoDiretoFuncao
from .services_consolidacao.consolidacao_service import ConsolidacaoService
import json
import logging

logger = logging.getLogger('custo_direto')


class DashboardConsolidadoView(TemplateView):
    """
    Dashboard otimizado usando consolidações pré-calculadas.
    """
    template_name = "dashboard/dashboard_consolidado.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtros da URL
        contrato_id = self.request.GET.get('contrato')
        
        # Buscar contratos disponíveis
        contratos = CadastroContrato.objects.filter(
            consolidacao_custos__isnull=False
        ).distinct().order_by('contrato')
        
        if not contratos.exists():
            contratos = CadastroContrato.objects.all().order_by('contrato')
        
        context['contratos'] = contratos
        
        if contrato_id:
            context.update(self._get_dados_contrato(contrato_id))
        
        return context
    
    def _get_dados_contrato(self, contrato_id):
        """
        Obtém dados consolidados de um contrato específico.
        """
        try:
            # Usar service de consolidação para obter dados
            resumo_completo = ConsolidacaoService.obter_resumo_completo(contrato_id)
            
            # Dados básicos do contrato
            contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
            consolidacao = resumo_completo['contrato']
            
            # Preparar dados para gráficos
            dados_custos_categoria = {
                'labels': ['Mão de Obra', 'Veículos', 'Combustível', 'Equipamentos'],
                'valores': [
                    float(consolidacao.custo_mao_obra),
                    float(consolidacao.custo_veiculos),
                    float(consolidacao.custo_combustivel),
                    float(consolidacao.custo_equipamentos)
                ]
            }
            
            # Dados por regional
            dados_regionais = []
            for regional in resumo_completo['por_regional']:
                dados_regionais.append({
                    'nome': regional['regional__nome'],
                    'custo_total': float(regional['total_mao_obra']),
                    'funcionarios': regional['total_funcionarios'],
                    'equipes': float(regional['total_equipes']) if regional['total_equipes'] else 0
                })
            
            # Dados por escopo
            dados_escopos = []
            for escopo in resumo_completo['por_escopo']:
                dados_escopos.append({
                    'nome': escopo['escopo__nome'],
                    'custo_total': float(escopo['total_mao_obra']),
                    'funcionarios': escopo['total_funcionarios']
                })
            
            # Top funções com maior custo
            top_funcoes = []
            for funcao in resumo_completo['top_custos']:
                top_funcoes.append({
                    'nome': funcao['funcao__nome'],
                    'custo_total': float(funcao['total_custo']),
                    'funcionarios': funcao['total_funcionarios'],
                    'salario_base': float(funcao['funcao__salario'])
                })
            
            # Dados de equipamentos detalhados
            dados_equipamentos = self._get_dados_equipamentos_detalhados(consolidacao)
            
            return {
                'contrato_selecionado': contrato,
                'consolidacao': consolidacao,
                'dados_custos_categoria': dados_custos_categoria,
                'dados_regionais': dados_regionais,
                'dados_escopos': dados_escopos,
                'top_funcoes': top_funcoes,
                'dados_equipamentos': dados_equipamentos,
                'resumo_encargos': resumo_completo['encargos_sociais'],
                'timestamp_atualizacao': resumo_completo['timestamp'].strftime('%d/%m/%Y %H:%M')
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados do contrato {contrato_id}: {e}")
            return {
                'erro': str(e),
                'contrato_selecionado': None
            }
    
    def _get_dados_equipamentos_detalhados(self, consolidacao):
        """
        Prepara dados detalhados de equipamentos para gráficos.
        """
        return {
            'labels': ['EPI', 'EPC', 'Ferramentas', 'TI', 'Desp. TI', 'Materiais', 'Diversas'],
            'valores': [
                float(consolidacao.custo_epi),
                float(consolidacao.custo_epc),
                float(consolidacao.custo_ferramentas),
                float(consolidacao.custo_equipamentos_ti),
                float(consolidacao.custo_despesas_ti),
                float(consolidacao.custo_materiais_consumo),
                float(consolidacao.custo_despesas_diversas)
            ],
            'total': float(consolidacao.custo_equipamentos)
        }


class ConsolidacaoAPIView(TemplateView):
    """
    API para fornecer dados de consolidação via AJAX.
    """
    
    def get(self, request, *args, **kwargs):
        contrato_id = request.GET.get('contrato_id')
        tipo = request.GET.get('tipo', 'contrato')  # contrato, regional, escopo, equipe
        
        if not contrato_id:
            return JsonResponse({'erro': 'Contrato obrigatório'}, status=400)
        
        try:
            if tipo == 'contrato':
                consolidacao = ConsolidacaoService.consolidar_contrato(contrato_id)
                return JsonResponse({
                    'custo_total': float(consolidacao.custo_total),
                    'custo_mao_obra': float(consolidacao.custo_mao_obra),
                    'custo_veiculos': float(consolidacao.custo_veiculos),
                    'custo_equipamentos': float(consolidacao.custo_equipamentos),
                    'total_funcionarios': consolidacao.total_funcionarios,
                    'total_equipes': float(consolidacao.total_equipes),
                    'data_consolidacao': consolidacao.data_consolidacao.isoformat()
                })
            
            elif tipo == 'regional':
                regionais = ConsolidacaoService.consolidar_todas_regionais(contrato_id)
                dados = []
                for regional in regionais:
                    dados.append({
                        'nome': regional.regional.nome,
                        'custo_total': float(regional.custo_total),
                        'funcionarios': regional.total_funcionarios,
                        'equipes': float(regional.total_equipes)
                    })
                return JsonResponse({'regionais': dados})
            
            elif tipo == 'resumo':
                resumo = ConsolidacaoService.obter_resumo_completo(contrato_id)
                # Serializar dados básicos
                return JsonResponse({
                    'custo_total': float(resumo['contrato'].custo_total),
                    'por_regional': list(resumo['por_regional']),
                    'por_escopo': list(resumo['por_escopo']),
                    'top_funcoes': list(resumo['top_custos']),
                    'timestamp': resumo['timestamp'].isoformat()
                })
            
            else:
                return JsonResponse({'erro': 'Tipo inválido'}, status=400)
                
        except Exception as e:
            logger.error(f"Erro na API de consolidação: {e}")
            return JsonResponse({'erro': str(e)}, status=500)


class RecalcularConsolidacaoView(TemplateView):
    """
    View para trigger manual de recálculo de consolidação.
    """
    
    def post(self, request, *args, **kwargs):
        contrato_id = request.POST.get('contrato_id')
        force_refresh = request.POST.get('force_refresh', 'false').lower() == 'true'
        
        if not contrato_id:
            return JsonResponse({'erro': 'Contrato obrigatório'}, status=400)
        
        try:
            # Invalidar cache
            ConsolidacaoService.invalidar_cache_contrato(contrato_id)
            
            # Recalcular
            if force_refresh:
                consolidacao = ConsolidacaoService.consolidar_contrato(contrato_id, force_refresh=True)
                ConsolidacaoService.consolidar_todas_regionais(contrato_id, force_refresh=True)
                mensagem = "Consolidação recalculada com sucesso!"
            else:
                consolidacao = ConsolidacaoService.recalcular_tudo_incremental(contrato_id)
                mensagem = "Consolidação incremental executada!"
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': mensagem,
                'custo_total': float(consolidacao.custo_total),
                'data_consolidacao': consolidacao.data_consolidacao.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Erro ao recalcular consolidação: {e}")
            return JsonResponse({
                'sucesso': False,
                'erro': str(e)
            }, status=500)