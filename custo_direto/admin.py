from django.contrib import admin
from .models import CustoDireto, CustoDiretoFuncao

@admin.register(CustoDiretoFuncao)
class CustoDiretoFuncaoAdmin(admin.ModelAdmin):
    list_display = (
        'contrato', 'funcao_equipe', 'quantidade_funcionarios',
        'salario_base', 'custo_total',
        'valor_grupo_a', 'valor_grupo_b', 'valor_grupo_c', 'valor_grupo_d', 'valor_total_encargos',
        'updated_at'
    )
    list_filter = ('contrato', 'funcao_equipe')
    search_fields = ('contrato__nome', 'funcao_equipe__nome')


@admin.register(CustoDireto)
class CustoDiretoAdmin(admin.ModelAdmin):
    list_display = ('contrato', 'custo_total', 'updated_at')
    search_fields = ('contrato__nome',)
