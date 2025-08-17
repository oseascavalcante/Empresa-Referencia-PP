from django.contrib import admin
from .models import TipoVeiculo, PrecoCombustivel, Veiculo, AtribuicaoVeiculo


@admin.register(TipoVeiculo)
class TipoVeiculoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'created_at']
    list_filter = ['categoria', 'created_at']
    search_fields = ['nome', 'descricao']
    ordering = ['categoria', 'nome']


@admin.register(PrecoCombustivel)
class PrecoCombustivelAdmin(admin.ModelAdmin):
    list_display = ['contrato', 'tipo_combustivel', 'preco_por_litro', 'updated_at']
    list_filter = ['tipo_combustivel', 'contrato', 'created_at']
    search_fields = ['contrato__contrato', 'contrato__concessionaria']
    ordering = ['contrato', 'tipo_combustivel']


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['tipo_veiculo', 'contrato', 'valor_aquisicao', 'tipo_combustivel', 'eficiencia_km_litro']
    list_filter = ['tipo_veiculo__categoria', 'tipo_combustivel', 'contrato']
    search_fields = ['tipo_veiculo__nome', 'contrato__contrato']
    ordering = ['contrato', 'tipo_veiculo__nome']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('contrato', 'tipo_veiculo')
        }),
        ('Dados Financeiros', {
            'fields': ('valor_aquisicao', 'vida_util_meses', 'custo_mensal_seguro', 'custo_mensal_manutencao')
        }),
        ('Dados de Combustível', {
            'fields': ('tipo_combustivel', 'eficiencia_km_litro', 'km_por_mes')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        })
    )


@admin.register(AtribuicaoVeiculo)
class AtribuicaoVeiculoAdmin(admin.ModelAdmin):
    list_display = ['veiculo', 'regional', 'escopo', 'quantidade', 'contrato']
    list_filter = ['contrato', 'regional', 'escopo', 'veiculo__tipo_veiculo__categoria']
    search_fields = ['veiculo__tipo_veiculo__nome', 'regional__nome', 'escopo__nome']
    ordering = ['contrato', 'regional', 'escopo']
