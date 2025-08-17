from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib import messages
from django.db import transaction
from cad_contrato.models import CadastroContrato
from cadastro_equipe.models import Equipe, ComposicaoEquipe
from .models import EquipamentoVidaUtil, EquipamentoMensal, EquipamentoEquipe
import json
import logging

logger = logging.getLogger(__name__)


class BaseEquipamentoView(TemplateView):
    """View base para todas as categorias de equipamentos"""
    
    def dispatch(self, request, *args, **kwargs):
        # Busca o contrato da sessão ou da URL
        contrato_id = self.kwargs.get('contrato_id') or request.session.get('contrato_id')
        if not contrato_id:
            messages.error(request, 'Selecione um contrato primeiro.')
            return redirect('selecionar_contrato')
        
        self.contrato = get_object_or_404(CadastroContrato, pk=contrato_id)
        request.session['contrato_id'] = contrato_id
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar equipes que estão nas composições ativas do contrato
        equipes_ativas_ids = ComposicaoEquipe.objects.filter(
            contrato=self.contrato,
            quantidade_equipes__gt=0
        ).values_list('equipe_id', flat=True).distinct()
        
        equipes_ativas = Equipe.objects.filter(
            id__in=equipes_ativas_ids
        ).order_by('nome')
        
        context.update({
            'contrato': self.contrato,
            'equipes': equipes_ativas,
        })
        return context


class EPIView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'EPI',
            'titulo': 'EPI - Equipamentos de Proteção Individual',
            'equipamentos': EquipamentoVidaUtil.objects.filter(
                contrato=self.contrato, 
                categoria='EPI'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'vida_util'
        })
        return context


class EPCView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'EPC',
            'titulo': 'EPC - Equipamentos de Proteção Coletiva',
            'equipamentos': EquipamentoVidaUtil.objects.filter(
                contrato=self.contrato, 
                categoria='EPC'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'vida_util'
        })
        return context


class FerramentasView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'FERRAMENTAS',
            'titulo': 'Ferramentas',
            'equipamentos': EquipamentoVidaUtil.objects.filter(
                contrato=self.contrato, 
                categoria='FERRAMENTAS'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'vida_util'
        })
        return context


class EquipamentosTIView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'EQUIPAMENTOS_TI',
            'titulo': 'Equipamentos TI',
            'equipamentos': EquipamentoVidaUtil.objects.filter(
                contrato=self.contrato, 
                categoria='EQUIPAMENTOS_TI'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'vida_util'
        })
        return context


class DespesasTIView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'DESPESAS_TI',
            'titulo': 'Despesas TI',
            'equipamentos': EquipamentoMensal.objects.filter(
                contrato=self.contrato, 
                categoria='DESPESAS_TI'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'mensal'
        })
        return context


class MateriaisConsumoView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'MATERIAIS_CONSUMO',
            'titulo': 'Materiais de Consumo',
            'equipamentos': EquipamentoMensal.objects.filter(
                contrato=self.contrato, 
                categoria='MATERIAIS_CONSUMO'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'mensal'
        })
        return context


class DespesasDiversasView(BaseEquipamentoView):
    template_name = 'equipamentos/base_equipamentos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categoria': 'DESPESAS_DIVERSAS',
            'titulo': 'Despesas Diversas',
            'equipamentos': EquipamentoMensal.objects.filter(
                contrato=self.contrato, 
                categoria='DESPESAS_DIVERSAS'
            ).prefetch_related('vinculacoes_equipe__equipe'),
            'tipo_equipamento': 'mensal'
        })
        return context


def salvar_equipamentos(request):
    """View para salvar equipamentos via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        data = json.loads(request.body)
        categoria = data.get('categoria')
        tipo_equipamento = data.get('tipo_equipamento')
        equipamentos_data = data.get('equipamentos', [])
        
        contrato_id = request.session.get('contrato_id')
        if not contrato_id:
            return JsonResponse({'success': False, 'message': 'Contrato não encontrado'})
        
        contrato = get_object_or_404(CadastroContrato, pk=contrato_id)
        
        with transaction.atomic():
            # Remove equipamentos existentes da categoria e suas vinculações
            if tipo_equipamento == 'vida_util':
                # Remove vinculações primeiro
                equipamentos_existentes = EquipamentoVidaUtil.objects.filter(
                    contrato=contrato, 
                    categoria=categoria
                )
                for eq in equipamentos_existentes:
                    EquipamentoEquipe.objects.filter(equipamento_vida_util=eq).delete()
                
                # Remove equipamentos
                equipamentos_existentes.delete()
            else:
                # Remove vinculações primeiro
                equipamentos_existentes = EquipamentoMensal.objects.filter(
                    contrato=contrato, 
                    categoria=categoria
                )
                for eq in equipamentos_existentes:
                    EquipamentoEquipe.objects.filter(equipamento_mensal=eq).delete()
                
                # Remove equipamentos
                equipamentos_existentes.delete()
            
            # Cria novos equipamentos e vinculações
            for eq_data in equipamentos_data:
                if not eq_data.get('descricao'):
                    continue
                
                # Cria o equipamento
                if tipo_equipamento == 'vida_util':
                    equipamento = EquipamentoVidaUtil.objects.create(
                        contrato=contrato,
                        categoria=categoria,
                        descricao=eq_data['descricao'],
                        vida_util_meses=int(eq_data.get('vida_util_meses', 1)),
                        valor_unitario=float(eq_data.get('valor_unitario', 0)),
                        quantidade=1  # Quantidade padrão, não mais usada para cálculos
                    )
                else:
                    equipamento = EquipamentoMensal.objects.create(
                        contrato=contrato,
                        categoria=categoria,
                        descricao=eq_data['descricao'],
                        valor_mensal=float(eq_data.get('valor_mensal', 0)),
                        quantidade=1  # Quantidade padrão, não mais usada para cálculos
                    )
                
                # Cria vinculações com equipes
                equipes_data = eq_data.get('equipes', {})
                for equipe_id, quantidade in equipes_data.items():
                    if quantidade > 0:
                        try:
                            equipe = Equipe.objects.get(id=equipe_id, contrato=contrato)
                            
                            # Define os parâmetros da vinculação baseado no tipo do equipamento
                            if tipo_equipamento == 'vida_util':
                                kwargs = {
                                    'contrato': contrato,
                                    'equipe': equipe,
                                    'equipamento_vida_util': equipamento,
                                    'quantidade_por_equipe': int(quantidade)
                                }
                            else:
                                kwargs = {
                                    'contrato': contrato,
                                    'equipe': equipe,
                                    'equipamento_mensal': equipamento,
                                    'quantidade_por_equipe': int(quantidade)
                                }
                            
                            EquipamentoEquipe.objects.create(**kwargs)
                            
                        except Equipe.DoesNotExist:
                            logger.warning(f"Equipe com ID {equipe_id} não encontrada")
        
        return JsonResponse({
            'success': True, 
            'message': f'Equipamentos da categoria {categoria} salvos com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao salvar equipamentos: {e}")
        return JsonResponse({
            'success': False, 
            'message': f'Erro ao salvar: {str(e)}'
        })


def vincular_equipamento_equipe(request):
    """View para vincular equipamentos às equipes"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        data = json.loads(request.body)
        equipamento_id = data.get('equipamento_id')
        tipo_equipamento = data.get('tipo_equipamento')
        equipe_id = data.get('equipe_id')
        quantidade = int(data.get('quantidade', 1))
        
        equipe = get_object_or_404(Equipe, pk=equipe_id)
        
        # Remove vinculação existente se houver
        EquipamentoEquipe.objects.filter(
            equipe=equipe,
            **{f'equipamento_{tipo_equipamento}_id': equipamento_id}
        ).delete()
        
        # Cria nova vinculação
        kwargs = {
            'equipe': equipe,
            'quantidade_por_equipe': quantidade,
            f'equipamento_{tipo_equipamento}_id': equipamento_id
        }
        
        EquipamentoEquipe.objects.create(**kwargs)
        
        return JsonResponse({
            'success': True,
            'message': 'Equipamento vinculado à equipe com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao vincular equipamento: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao vincular: {str(e)}'
        })


def excluir_equipamento(request, equipamento_id):
    """View para excluir equipamento"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    try:
        tipo_equipamento = request.POST.get('tipo_equipamento')
        
        if tipo_equipamento == 'vida_util':
            equipamento = get_object_or_404(EquipamentoVidaUtil, pk=equipamento_id)
        else:
            equipamento = get_object_or_404(EquipamentoMensal, pk=equipamento_id)
        
        equipamento.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Equipamento excluído com sucesso!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao excluir equipamento: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Erro ao excluir: {str(e)}'
        })
