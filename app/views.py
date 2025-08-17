from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from cad_contrato.models import CadastroContrato
from .services.form_status_service import FormStatusService, ProgressCalculatorService
from .config.form_definitions import get_active_categories
from .config.features import get_feature_context, is_feature_enabled

def home(request):
    return render(request, "home.html")

def menu_cadastro_estrutura(request, filter_category=None):
    """
    View refatorada para usar sistema dinâmico de formulários.
    Carrega configurações, verifica status e calcula progresso automaticamente.
    Suporta filtro por categoria específica (ex: admin).
    """
    contrato_id = request.session.get('contrato_id')
    if not contrato_id:
        return redirect(f"{reverse_lazy('selecionar_contrato')}?next={reverse_lazy('menu_cadastro_estrutura')}")
    
    contrato = CadastroContrato.objects.get(pk=contrato_id)
    
    # Carrega configuração dinâmica de formulários
    all_categorias = get_active_categories()
    
    # Filtra categoria se especificada
    if filter_category:
        categorias_formularios = {filter_category: all_categorias[filter_category]} if filter_category in all_categorias else {}
    else:
        # Remove categoria admin da visualização normal do menu
        categorias_formularios = {k: v for k, v in all_categorias.items() if k != 'admin'}
    
    # Inicializa services
    status_service = FormStatusService()
    
    # Verifica status completo de todos os formulários
    status_completo = status_service.verificar_status_completo(contrato.pk)
    
    # Calcula progresso geral
    progresso = ProgressCalculatorService.calcular_progresso_geral(status_completo)
    
    # Calcula próximos passos sugeridos
    proximos_passos = ProgressCalculatorService.calcular_proximos_passos(status_completo)
    
    # Adiciona URL parameters para formulários que precisam de contrato_id
    for categoria in categorias_formularios.values():
        for form in categoria['forms']:
            # Adiciona contrato_id para formulários que requerem
            if form.get('url_requires_contrato', False):
                form['url_params'] = {'contrato_id': contrato.pk}
            else:
                form['url_params'] = {}
    
    # Prepara context com todas as informações
    context = {
        'contrato': contrato,
        'categorias_formularios': categorias_formularios,
        'status_completo': status_completo,
        'progresso': progresso,
        'proximos_passos': proximos_passos[:3],  # Apenas os 3 primeiros
        
        # Estatísticas para template
        'estatisticas': status_completo['estatisticas'],
        
        # Flags de features
        **get_feature_context(),
        
        # Helpers para template
        'show_progress_bar': is_feature_enabled('menu_progress_bar'),
        'show_status_indicators': is_feature_enabled('menu_status_indicators'),
        'modern_design': is_feature_enabled('menu_modern_design'),
    }
    
    return render(request, 'menu_cadastro_estrutura.html', context)