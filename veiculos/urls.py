from django.urls import path
from .views import (
    TipoVeiculoCreateView, TipoVeiculoUpdateView, TipoVeiculoDeleteView,
    PrecoCombustivelCreateView, PrecoCombustivelUpdateView, PrecoCombustivelDeleteView,
    VeiculoCreateView, VeiculoUpdateView, VeiculoDeleteView, AtribuicaoVeiculoView
)

urlpatterns = [
    # Tipos de Veículos (Master Data)
    path('tipos/', TipoVeiculoCreateView.as_view(), name='cadastrar_tipo_veiculo'),
    path('tipos/editar/<int:pk>/', TipoVeiculoUpdateView.as_view(), name='editar_tipo_veiculo'),
    path('tipos/excluir/<int:pk>/', TipoVeiculoDeleteView.as_view(), name='excluir_tipo_veiculo'),
    
    # Preços de Combustível por Contrato
    path('precos-combustivel/<int:contrato_id>/', PrecoCombustivelCreateView.as_view(), name='configurar_precos_combustivel'),
    path('precos-combustivel/editar/<int:pk>/', PrecoCombustivelUpdateView.as_view(), name='editar_preco_combustivel'),
    path('precos-combustivel/excluir/<int:pk>/', PrecoCombustivelDeleteView.as_view(), name='excluir_preco_combustivel'),
    
    # Veículos por Contrato
    path('cadastrar/<int:contrato_id>/', VeiculoCreateView.as_view(), name='cadastrar_veiculo'),
    path('editar/<int:pk>/', VeiculoUpdateView.as_view(), name='editar_veiculo'),
    path('excluir/<int:pk>/', VeiculoDeleteView.as_view(), name='excluir_veiculo'),
    
    # Atribuição de Veículos
    path('atribuir/<int:contrato_id>/', AtribuicaoVeiculoView.as_view(), name='atribuir_veiculos'),
    path('atribuir/<int:contrato_id>/json/<int:atribuicao_id>/', AtribuicaoVeiculoView.as_view(), name='atribuicao_json'),
    path('atribuir/<int:contrato_id>/editar/<int:atribuicao_id>/', AtribuicaoVeiculoView.as_view(), name='editar_atribuicao'),
    path('atribuir/<int:contrato_id>/excluir/<int:atribuicao_id>/', AtribuicaoVeiculoView.as_view(), name='excluir_atribuicao'),
]