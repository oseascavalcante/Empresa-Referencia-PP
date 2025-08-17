from django.urls import path
from .views import (
    EPIView, EPCView, FerramentasView, EquipamentosTIView,
    DespesasTIView, MateriaisConsumoView, DespesasDiversasView,
    salvar_equipamentos, vincular_equipamento_equipe, excluir_equipamento
)

urlpatterns = [
    # Grupos com vida útil
    path('epi/', EPIView.as_view(), name='equipamentos_epi'),
    path('epc/', EPCView.as_view(), name='equipamentos_epc'),
    path('ferramentas/', FerramentasView.as_view(), name='equipamentos_ferramentas'),
    path('equipamentos-ti/', EquipamentosTIView.as_view(), name='equipamentos_ti'),
    
    # Grupos mensais
    path('despesas-ti/', DespesasTIView.as_view(), name='despesas_ti'),
    path('materiais-consumo/', MateriaisConsumoView.as_view(), name='materiais_consumo'),
    path('despesas-diversas/', DespesasDiversasView.as_view(), name='despesas_diversas'),
    
    # AJAX endpoints
    path('salvar/', salvar_equipamentos, name='salvar_equipamentos'),
    path('vincular/', vincular_equipamento_equipe, name='vincular_equipamento_equipe'),
    path('excluir/<int:equipamento_id>/', excluir_equipamento, name='excluir_equipamento'),
]