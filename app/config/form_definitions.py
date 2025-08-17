"""
Configuração extensível para formulários do menu de cadastro de estrutura.
Esta estrutura permite adicionar novos formulários facilmente sem modificar o código core.
"""

FORM_CATEGORIES = {
    'admin': {
        'title': 'Administração do Sistema',
        'subtitle': 'Configurações administrativas e dados mestres',
        'order': 0,
        'icon': 'fas fa-shield-alt',
        'color': 'danger',
        'forms': [
            {
                'id': 'tipos_veiculos',
                'title': 'Cadastrar Tipos de Veículos',
                'description': 'Cadastre tipos de veículos (master data)',
                'url_name': 'cadastrar_tipo_veiculo',
                'icon': 'fas fa-cogs',
                'checker_method': 'verificar_tipos_veiculos',
                'order': 1,
                'required': True
            }
        ]
    },
    'estrutura_basica': {
        'title': 'Estrutura Básica',
        'subtitle': 'Configurações fundamentais do contrato',
        'order': 1,
        'icon': 'fas fa-building',
        'color': 'primary',
        'forms': [
            {
                'id': 'regionais',
                'title': 'Regionais',
                'description': 'Cadastre as regionais do contrato',
                'url_name': 'adicionar_regional',
                'icon': 'fas fa-map-marker-alt',
                'checker_method': 'verificar_regionais',
                'order': 1,
                'required': True,
                'url_requires_contrato': True
            },
            {
                'id': 'equipes',
                'title': 'Equipes',
                'description': 'Configure as equipes de trabalho',
                'url_name': 'adicionar_equipe',
                'icon': 'fas fa-users',
                'checker_method': 'verificar_equipes',
                'order': 2,
                'required': True
            },
            {
                'id': 'escopos',
                'title': 'Escopo de Atividades',
                'description': 'Configure os escopos de atividades',
                'url_name': 'adicionar_escopo',
                'icon': 'fas fa-tasks',
                'checker_method': 'verificar_escopos',
                'order': 3,
                'required': True
            }
        ]
    },
    'estrutura_pessoal': {
        'title': 'Estrutura Pessoal',
        'subtitle': 'Configurações de pessoal e remuneração',
        'order': 2,
        'icon': 'fas fa-user-tie',
        'color': 'secondary',
        'forms': [
            {
                'id': 'funcoes',
                'title': 'Funções/Salários',
                'description': 'Defina funções e valores salariais',
                'url_name': 'adicionar_funcao',
                'icon': 'fas fa-briefcase',
                'checker_method': 'verificar_funcoes',
                'order': 1,
                'required': True
            },
            {
                'id': 'encargos_sociais',
                'title': 'Encargos Sociais',
                'description': 'Configure os encargos sociais e tributos',
                'url_name': 'grupo_abc_form',
                'icon': 'fas fa-percentage',
                'checker_method': 'verificar_encargos_sociais',
                'order': 2,
                'required': True,
                'url_requires_contrato': True
            },
            {
                'id': 'beneficios',
                'title': 'Benefícios',
                'description': 'Configure benefícios dos colaboradores',
                'url_name': 'editar_beneficios',
                'icon': 'fas fa-gift',
                'checker_method': 'verificar_beneficios',
                'order': 3,
                'required': True,
                'url_requires_contrato': True
            }
        ]
    },
    'equipamentos_materiais': {
        'title': 'Equipamentos, Ferramentas e Materiais',
        'subtitle': 'Gestão de equipamentos e materiais',
        'order': 3,
        'icon': 'fas fa-tools',
        'color': 'info',
        'forms': [
            {
                'id': 'epi',
                'title': 'EPI',
                'description': 'Equipamentos de Proteção Individual',
                'url_name': 'equipamentos_epi',
                'icon': 'fas fa-hard-hat',
                'checker_method': 'verificar_epi',
                'order': 1,
                'required': False
            },
            {
                'id': 'epc',
                'title': 'EPC',
                'description': 'Equipamentos de Proteção Coletiva',
                'url_name': 'equipamentos_epc',
                'icon': 'fas fa-shield-alt',
                'checker_method': 'verificar_epc',
                'order': 2,
                'required': False
            },
            {
                'id': 'ferramentas',
                'title': 'Ferramentas',
                'description': 'Ferramentas de trabalho',
                'url_name': 'equipamentos_ferramentas',
                'icon': 'fas fa-wrench',
                'checker_method': 'verificar_ferramentas',
                'order': 3,
                'required': False
            },
            {
                'id': 'equipamentos_ti',
                'title': 'Equipamentos TI',
                'description': 'Equipamentos de Tecnologia',
                'url_name': 'equipamentos_ti',
                'icon': 'fas fa-laptop',
                'checker_method': 'verificar_equipamentos_ti',
                'order': 4,
                'required': False
            },
            {
                'id': 'despesas_ti',
                'title': 'Despesas TI',
                'description': 'Despesas mensais de TI',
                'url_name': 'despesas_ti',
                'icon': 'fas fa-server',
                'checker_method': 'verificar_despesas_ti',
                'order': 5,
                'required': False
            },
            {
                'id': 'materiais_consumo',
                'title': 'Materiais',
                'description': 'Materiais de consumo',
                'url_name': 'materiais_consumo',
                'icon': 'fas fa-box',
                'checker_method': 'verificar_materiais_consumo',
                'order': 6,
                'required': False
            },
            {
                'id': 'despesas_diversas',
                'title': 'Despesas Diversas',
                'description': 'Outras despesas mensais',
                'url_name': 'despesas_diversas',
                'icon': 'fas fa-receipt',
                'checker_method': 'verificar_despesas_diversas',
                'order': 7,
                'required': False
            }
        ]
    },
    'veiculos_implementos': {
        'title': 'Veículos, Implementos e Equipamentos',
        'subtitle': 'Gestão de frota e equipamentos móveis',
        'order': 4,
        'icon': 'fas fa-truck',
        'color': 'success',
        'forms': [
            {
                'id': 'precos_combustivel',
                'title': 'Preços de Combustível',
                'description': 'Configure preços por tipo de combustível',
                'url_name': 'configurar_precos_combustivel',
                'icon': 'fas fa-gas-pump',
                'checker_method': 'verificar_precos_combustivel',
                'order': 1,
                'required': True,
                'url_requires_contrato': True
            },
            {
                'id': 'cadastrar_veiculos',
                'title': 'Parametrizar Veículos do Contrato',
                'description': 'Cadastro de Parâmetros Técnicos e Custos Operacionais',
                'url_name': 'cadastrar_veiculo',
                'icon': 'fas fa-car',
                'checker_method': 'verificar_cadastrar_veiculos',
                'order': 2,
                'required': True,
                'url_requires_contrato': True
            },
            {
                'id': 'atribuir_veiculos',
                'title': 'Atribuir Veículos',
                'description': 'Atribua veículos às equipes por quantidade',
                'url_name': 'atribuir_veiculos',
                'icon': 'fas fa-route',
                'checker_method': 'verificar_atribuir_veiculos',
                'order': 3,
                'required': False,
                'url_requires_contrato': True
            }
        ]
    }
}

# Formulários futuros podem ser facilmente adicionados aqui
FUTURE_FORM_CATEGORIES = {
    'custos_indiretos': {
        'title': 'Custos Indiretos',
        'subtitle': 'Custos administrativos e terceirizados',
        'order': 3,
        'icon': 'fas fa-calculator',
        'color': 'warning',
        'enabled': False,  # Feature flag
        'forms': [
            {
                'id': 'materiais_construcao',
                'title': 'Materiais de Construção',
                'description': 'Materiais para obras e construção',
                'url_name': 'materiais_construcao',  # Futuro
                'icon': 'fas fa-hammer',
                'checker_method': 'verificar_materiais_construcao',
                'order': 1,
                'required': False
            },
            {
                'id': 'terceirizados',
                'title': 'Serviços Terceirizados',
                'description': 'Empresas e serviços terceirizados',
                'url_name': 'servicos_terceirizados',  # Futuro
                'icon': 'fas fa-handshake',
                'checker_method': 'verificar_terceirizados',
                'order': 2,
                'required': False
            }
        ]
    },
    'margem_precificacao': {
        'title': 'Margem e Precificação',
        'subtitle': 'Configurações comerciais e financeiras',
        'order': 4,
        'icon': 'fas fa-percentage',
        'color': 'success',
        'enabled': False,  # Feature flag
        'forms': [
            {
                'id': 'margem_lucro',
                'title': 'Margem de Lucro',
                'description': 'Configurar margem de lucro do projeto',
                'url_name': 'configurar_margem',  # Futuro
                'icon': 'fas fa-chart-line',
                'checker_method': 'verificar_margem',
                'order': 1,
                'required': False
            }
        ]
    }
}


def get_active_categories():
    """Retorna categorias ativas baseadas em feature flags"""
    active_categories = FORM_CATEGORIES.copy()
    
    # Adiciona categorias futuras se habilitadas
    for category_id, category in FUTURE_FORM_CATEGORIES.items():
        if category.get('enabled', False):
            active_categories[category_id] = category
    
    return active_categories


def get_all_forms():
    """Retorna todos os formulários de todas as categorias ativas"""
    forms = []
    for category in get_active_categories().values():
        forms.extend(category['forms'])
    return forms


def get_form_by_id(form_id):
    """Busca um formulário específico pelo ID"""
    for form in get_all_forms():
        if form['id'] == form_id:
            return form
    return None


def get_required_forms():
    """Retorna apenas os formulários obrigatórios"""
    return [form for form in get_all_forms() if form.get('required', False)]


def calculate_total_forms():
    """Calcula o total de formulários disponíveis"""
    return len(get_all_forms())


def calculate_required_forms():
    """Calcula o total de formulários obrigatórios"""
    return len(get_required_forms())