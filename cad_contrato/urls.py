from django.urls import path, include
from .views import ContractCreateView, lista_formularios, menu_principal, abrir_contratos, DetailContratosView
from .views import SelecionarContratoView, UpdateContratoView
from .views import MenuDespesasView

urlpatterns = [
    path('cadastro-contrato/new/', ContractCreateView.as_view(), name='cadastro_contrato'),
    path("lista-formularios/", lista_formularios, name="lista_formularios"),
    path('menu/', menu_principal, name="menu_principal"),
    path('abrir/', abrir_contratos, name='abrir_contratos'),
    path("selecionar/", SelecionarContratoView.as_view(), name="selecionar_contrato"),
    path('menu-despesas/<int:contrato_id>/', MenuDespesasView.as_view(), name='menu_despesas'),
    path('detalhes-contrato/<int:pk>/', DetailContratosView.as_view(), name='detalhes_contrato'),
    path('editar-contrato/<int:pk>/', UpdateContratoView.as_view(), name='editar_contrato'),
    ]

