from django.urls import path
from .views import EquipeCreateView, FuncaoCreateView, ComposicaoEquipeView, ComposicaoEquipeDeleteView, ComposicaoEquipeUpdateView, ComposicaoEquipeDetailView, ComposicaoEquipeJSONView 

urlpatterns = [
    path('adicionar-equipe/', EquipeCreateView.as_view(), name='adicionar_equipe'),
    path('adicionar-funcao/', FuncaoCreateView.as_view(), name='adicionar_funcao'),
    path('composicao/<int:contrato_id>/', ComposicaoEquipeView.as_view(), name='composicao_equipe'),
    path('composicao/<uuid:pk>/excluir/', ComposicaoEquipeDeleteView.as_view(), name='excluir_composicao'),
    path('composicao/<uuid:pk>/editar/', ComposicaoEquipeUpdateView.as_view(), name='editar_composicao'),
    path('composicao/<uuid:pk>/detalhes/', ComposicaoEquipeDetailView.as_view(), name='detalhes_equipe'),  # Nova rota
    path('composicao/<uuid:pk>/json/', ComposicaoEquipeJSONView.as_view(), name='composicao_equipe_json'),
    
]
