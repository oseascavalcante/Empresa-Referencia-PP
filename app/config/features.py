"""
Sistema de feature flags para controlar funcionalidades do sistema.
Permite ativar/desativar recursos gradualmente.
"""

FEATURE_FLAGS = {
    # Funcionalidades do menu principal
    'menu_progress_bar': True,
    'menu_status_indicators': True,
    'menu_modern_design': True,
    
    # Futuras categorias de formulários
    'custos_indiretos_enabled': False,
    'margem_precificacao_enabled': False,
    'relatorios_avancados_enabled': False,
    
    # Funcionalidades avançadas
    'auto_save_progress': False,
    'form_validation_real_time': False,
    'notification_system': False,
    
    # Integrações futuras
    'api_external_integration': False,
    'export_advanced_formats': False,
    'dashboard_analytics': True,
}


def is_feature_enabled(feature_name):
    """
    Verifica se uma feature está habilitada.
    
    Args:
        feature_name (str): Nome da feature a ser verificada
        
    Returns:
        bool: True se a feature estiver habilitada, False caso contrário
    """
    return FEATURE_FLAGS.get(feature_name, False)


def get_enabled_features():
    """
    Retorna lista de todas as features habilitadas.
    
    Returns:
        list: Lista com nomes das features habilitadas
    """
    return [feature for feature, enabled in FEATURE_FLAGS.items() if enabled]


def get_all_features():
    """
    Retorna todas as features e seus status.
    
    Returns:
        dict: Dicionário com todas as features e seus status
    """
    return FEATURE_FLAGS.copy()


def enable_feature(feature_name):
    """
    Habilita uma feature específica.
    
    Args:
        feature_name (str): Nome da feature a ser habilitada
    """
    if feature_name in FEATURE_FLAGS:
        FEATURE_FLAGS[feature_name] = True
        return True
    return False


def disable_feature(feature_name):
    """
    Desabilita uma feature específica.
    
    Args:
        feature_name (str): Nome da feature a ser desabilitada
    """
    if feature_name in FEATURE_FLAGS:
        FEATURE_FLAGS[feature_name] = False
        return True
    return False


def get_feature_context():
    """
    Retorna context para templates com features habilitadas.
    
    Returns:
        dict: Context com features para uso em templates
    """
    return {
        'features': FEATURE_FLAGS,
        'is_feature_enabled': is_feature_enabled
    }