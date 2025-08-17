"""
Template tags customizados para trabalhar com dicionários nos templates.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Permite acessar item de dicionário usando chave variável no template.
    
    Uso: {{ mydict|get_item:key_variable }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def get_attr(obj, attr_name):
    """
    Permite acessar atributo de objeto usando nome variável.
    
    Uso: {{ myobj|get_attr:attr_name_variable }}
    """
    try:
        return getattr(obj, attr_name, None)
    except (AttributeError, TypeError):
        return None


@register.filter
def percentage(value, total):
    """
    Calcula percentual entre dois valores.
    
    Uso: {{ current_value|percentage:total_value }}
    """
    try:
        if total == 0:
            return 0
        return round((value / total) * 100, 1)
    except (TypeError, ZeroDivisionError):
        return 0


@register.simple_tag
def define(value):
    """
    Define uma variável no template.
    
    Uso: {% define "value" as my_var %}
    """
    return value