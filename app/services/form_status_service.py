"""
Service principal para gerenciar status de formulários e calcular progresso.
Centraliza toda a lógica de verificação de status e cálculo de progresso.
"""

from typing import Dict, List, Any, Tuple
from django.core.cache import cache
from .form_checkers import FormCheckerFactory, FormStatus
from ..config.form_definitions import get_active_categories, get_all_forms, get_required_forms


class FormStatusService:
    """
    Service principal para verificar status de formulários.
    Utiliza os checkers registrados para verificar o status de cada formulário.
    """
    
    def __init__(self):
        self.checker_factory = FormCheckerFactory()
    
    def verificar_status_formulario(self, form_id: str, contrato_id: int) -> Dict[str, Any]:
        """
        Verifica o status de um formulário específico.
        
        Args:
            form_id: ID do formulário
            contrato_id: ID do contrato
            
        Returns:
            dict: Status do formulário com detalhes
        """
        # Verifica se existe checker para este formulário
        if not self.checker_factory.has_checker(form_id):
            return {
                'status': FormStatus.NAO_APLICAVEL,
                'count': 0,
                'required_count': 0,
                'message': 'Formulário não implementado',
                'details': {}
            }
        
        # Cria checker e verifica status
        checker = self.checker_factory.create_checker(form_id)
        return checker.verificar_status(contrato_id)
    
    def verificar_status_categoria(self, categoria_id: str, contrato_id: int) -> Dict[str, Any]:
        """
        Verifica o status de todos os formulários de uma categoria.
        
        Args:
            categoria_id: ID da categoria
            contrato_id: ID do contrato
            
        Returns:
            dict: Status da categoria com detalhes de todos os formulários
        """
        categorias = get_active_categories()
        
        if categoria_id not in categorias:
            return {
                'status': FormStatus.NAO_APLICAVEL,
                'forms': {},
                'summary': {
                    'total': 0,
                    'completos': 0,
                    'parciais': 0,
                    'vazios': 0
                }
            }
        
        categoria = categorias[categoria_id]
        forms_status = {}
        summary = {
            'total': 0,
            'completos': 0,
            'parciais': 0,
            'vazios': 0
        }
        
        # Verifica status de cada formulário da categoria
        for form in categoria['forms']:
            form_id = form['id']
            status = self.verificar_status_formulario(form_id, contrato_id)
            forms_status[form_id] = status
            
            # Atualiza sumário
            summary['total'] += 1
            if status['status'] == FormStatus.COMPLETO:
                summary['completos'] += 1
            elif status['status'] == FormStatus.PARCIAL:
                summary['parciais'] += 1
            elif status['status'] == FormStatus.VAZIO:
                summary['vazios'] += 1
        
        # Determina status geral da categoria
        if summary['completos'] == summary['total']:
            categoria_status = FormStatus.COMPLETO
        elif summary['completos'] > 0 or summary['parciais'] > 0:
            categoria_status = FormStatus.PARCIAL
        else:
            categoria_status = FormStatus.VAZIO
        
        return {
            'status': categoria_status,
            'forms': forms_status,
            'summary': summary,
            'categoria_info': categoria
        }
    
    def verificar_status_completo(self, contrato_id: int) -> Dict[str, Any]:
        """
        Verifica o status completo de todos os formulários e categorias.
        
        Args:
            contrato_id: ID do contrato
            
        Returns:
            dict: Status completo do contrato
        """
        # Tenta buscar do cache primeiro
        cache_key = f"form_status_{contrato_id}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        categorias = get_active_categories()
        categorias_status = {}
        
        # Verifica status de cada categoria
        for categoria_id in categorias.keys():
            categorias_status[categoria_id] = self.verificar_status_categoria(categoria_id, contrato_id)
        
        # Calcula estatísticas gerais
        stats = self._calcular_estatisticas_gerais(categorias_status)
        
        result = {
            'categorias': categorias_status,
            'estatisticas': stats,
            'contrato_id': contrato_id,
            'timestamp': cache.get('current_timestamp', None)
        }
        
        # Cache por 5 minutos
        cache.set(cache_key, result, 300)
        
        return result
    
    def _calcular_estatisticas_gerais(self, categorias_status: Dict) -> Dict[str, Any]:
        """
        Calcula estatísticas gerais baseadas no status das categorias.
        """
        total_forms = 0
        completos = 0
        parciais = 0
        vazios = 0
        obrigatorios_completos = 0
        total_obrigatorios = 0
        
        forms_required = {f['id']: f['required'] for f in get_all_forms()}
        
        for categoria_data in categorias_status.values():
            for form_id, form_status in categoria_data['forms'].items():
                total_forms += 1
                
                # Verifica se é obrigatório
                is_required = forms_required.get(form_id, False)
                if is_required:
                    total_obrigatorios += 1
                    if form_status['status'] == FormStatus.COMPLETO:
                        obrigatorios_completos += 1
                
                # Conta status
                if form_status['status'] == FormStatus.COMPLETO:
                    completos += 1
                elif form_status['status'] == FormStatus.PARCIAL:
                    parciais += 1
                elif form_status['status'] == FormStatus.VAZIO:
                    vazios += 1
        
        # Calcula percentuais
        percentual_geral = (completos / total_forms * 100) if total_forms > 0 else 0
        percentual_obrigatorios = (obrigatorios_completos / total_obrigatorios * 100) if total_obrigatorios > 0 else 0
        
        return {
            'total_formularios': total_forms,
            'formularios_completos': completos,
            'formularios_parciais': parciais,
            'formularios_vazios': vazios,
            'total_obrigatorios': total_obrigatorios,
            'obrigatorios_completos': obrigatorios_completos,
            'percentual_geral': round(percentual_geral, 1),
            'percentual_obrigatorios': round(percentual_obrigatorios, 1)
        }
    
    def invalidar_cache(self, contrato_id: int):
        """
        Invalida o cache de status para um contrato específico.
        Deve ser chamado quando dados do contrato são modificados.
        """
        cache_key = f"form_status_{contrato_id}"
        cache.delete(cache_key)
    
    def get_forms_por_status(self, contrato_id: int, status: FormStatus) -> List[Dict]:
        """
        Retorna lista de formulários com um status específico.
        
        Args:
            contrato_id: ID do contrato
            status: Status desejado
            
        Returns:
            list: Lista de formulários com o status especificado
        """
        status_completo = self.verificar_status_completo(contrato_id)
        forms_filtrados = []
        
        for categoria_data in status_completo['categorias'].values():
            for form_id, form_status in categoria_data['forms'].items():
                if form_status['status'] == status:
                    # Busca informações do formulário na configuração
                    form_config = None
                    for form in get_all_forms():
                        if form['id'] == form_id:
                            form_config = form
                            break
                    
                    if form_config:
                        forms_filtrados.append({
                            'config': form_config,
                            'status': form_status
                        })
        
        return forms_filtrados


class ProgressCalculatorService:
    """
    Service para calcular progresso e métricas de preenchimento.
    """
    
    @staticmethod
    def calcular_progresso_geral(status_completo: Dict) -> Dict[str, Any]:
        """
        Calcula o progresso geral baseado no status completo.
        
        Args:
            status_completo: Resultado do verificar_status_completo
            
        Returns:
            dict: Métricas de progresso
        """
        stats = status_completo['estatisticas']
        
        return {
            'percentual_geral': stats['percentual_geral'],
            'percentual_obrigatorios': stats['percentual_obrigatorios'],
            'formularios_completos': stats['formularios_completos'],
            'total_formularios': stats['total_formularios'],
            'obrigatorios_completos': stats['obrigatorios_completos'],
            'total_obrigatorios': stats['total_obrigatorios'],
            'status_geral': ProgressCalculatorService._determinar_status_geral(stats)
        }
    
    @staticmethod
    def _determinar_status_geral(stats: Dict) -> str:
        """Determina o status geral baseado nas estatísticas"""
        if stats['percentual_obrigatorios'] == 100:
            return 'completo_obrigatorios'
        elif stats['percentual_geral'] == 100:
            return 'completo_total'
        elif stats['percentual_obrigatorios'] > 0:
            return 'em_progresso'
        else:
            return 'iniciando'
    
    @staticmethod
    def calcular_proximos_passos(status_completo: Dict) -> List[Dict]:
        """
        Sugere próximos passos baseado no status atual.
        
        Returns:
            list: Lista de sugestões de próximos passos
        """
        service = FormStatusService()
        contrato_id = status_completo['contrato_id']
        
        # Busca formulários obrigatórios vazios
        forms_obrigatorios_vazios = []
        forms_obrigatorios = get_required_forms()
        
        for form in forms_obrigatorios:
            status = service.verificar_status_formulario(form['id'], contrato_id)
            if status['status'] == FormStatus.VAZIO:
                forms_obrigatorios_vazios.append({
                    'form': form,
                    'prioridade': 'alta',
                    'motivo': 'Formulário obrigatório não preenchido'
                })
        
        # Busca formulários parciais
        forms_parciais = service.get_forms_por_status(contrato_id, FormStatus.PARCIAL)
        passos_parciais = [{
            'form': form_data['config'],
            'prioridade': 'media',
            'motivo': 'Formulário incompleto'
        } for form_data in forms_parciais]
        
        return forms_obrigatorios_vazios + passos_parciais