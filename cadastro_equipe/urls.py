from django.urls import path
from .views import EquipeCreateView, FuncaoCreateView, ComposicaoEquipeView

urlpatterns = [
    path('adicionar-equipe/', EquipeCreateView.as_view(), name='adicionar_equipe'),
    path('adicionar-funcao/', FuncaoCreateView.as_view(), name='adicionar_funcao'),
    path('composicao/<int:contrato_id>/', ComposicaoEquipeView.as_view(), name='composicao_equipe'),
]
