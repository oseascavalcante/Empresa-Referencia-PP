from django.urls import path
from .views import ContractCreateView, lista_formularios, menu_principal, abrir_contratos

urlpatterns = [
    path('cadastro-contrato/new/', ContractCreateView.as_view(), name='cadastro_contrato'),
    path("lista-formularios/", lista_formularios, name="lista_formularios"),
    path('menu/', menu_principal, name="menu_principal"),
    path('abrir/', abrir_contratos, name='abrir_contratos'),
]