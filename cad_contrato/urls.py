from django.urls import path
from .views import ContractCreateView, lista_formularios, menu_principal

urlpatterns = [
    path('cadastro-contrato/new/', ContractCreateView.as_view(), name='cadastro_contrato'),
    path("lista-formularios/", lista_formularios, name="lista_formularios"),
    path('menu/', menu_principal, name="menu_principal"),
]