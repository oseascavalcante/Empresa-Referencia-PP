from django.shortcuts import redirect
from django.urls import path

from .views import (
    EquipeCreateView,
    EscopoCreateView,
    EscopoDeleteView,
    EscopoUpdateView,
    FuncaoCreateView,
    FuncaoUpdateView,
    FuncaoDeleteView,
    ComposicaoEquipeView,
    ComposicaoEquipeDeleteView,
    ComposicaoEquipeUpdateView,
    ComposicaoEquipeDetailView,
    ComposicaoEquipeJSONView,
    EditarSalariosView,
    EquipeUpdateView,
    EquipeDeleteView
)

urlpatterns = [
    # -----------------------------
    # Equipe / Função
    # -----------------------------
    path('adicionar-equipe/', EquipeCreateView.as_view(), name='adicionar_equipe'),
    path('adicionar-funcao/', FuncaoCreateView.as_view(), name='adicionar_funcao'),
    path('editar-funcao/<int:pk>/', FuncaoUpdateView.as_view(), name='editar_funcao'),
    path('excluir-funcao/<int:pk>/', FuncaoDeleteView.as_view(), name='excluir_funcao'),

    # -----------------------------
    # Escopo
    # -----------------------------
    path('adicionar-escopo/', EscopoCreateView.as_view(), name='adicionar_escopo'),
    path('editar-escopo/<int:pk>/', EscopoUpdateView.as_view(), name='editar_escopo'),
    path('excluir-escopo/<int:pk>/', EscopoDeleteView.as_view(), name='excluir_escopo'),

    # -----------------------------
    # Composição de Equipe
    # -----------------------------
    path('composicao/<int:contrato_id>/', ComposicaoEquipeView.as_view(), name='composicao_equipe'),
    path('composicao/<uuid:pk>/excluir/', ComposicaoEquipeDeleteView.as_view(), name='excluir_composicao'),
    path('composicao/<uuid:pk>/editar/', ComposicaoEquipeUpdateView.as_view(), name='editar_composicao'),
    path('composicao/<uuid:pk>/detalhes/', ComposicaoEquipeDetailView.as_view(), name='detalhes_equipe'),
    path('composicao/<uuid:pk>/json/', ComposicaoEquipeJSONView.as_view(), name='composicao_equipe_json'),
    
    # -----------------------------
    # Editar Equipe
    # -----------------------------
    path('editar-equipe/<int:pk>/', EquipeUpdateView.as_view(), name='editar_equipe'),
    path('excluir-equipe/<int:pk>/', EquipeDeleteView.as_view(), name='excluir_equipe'),
  

    # -----------------------------
    # Salários (novas rotas da tela)
    # -----------------------------
    # Suporta /editar-salarios/?contrato=123 redirecionando para a rota canônica
    path(
        'editar-salarios/',
        lambda r: redirect('editar_salarios', contrato_id=r.GET.get('contrato')),
        name='editar_salarios_redirect',
    ),
    # Tela canônica com contrato na URL
    path('editar-salarios/<int:contrato_id>/', EditarSalariosView.as_view(), name='editar_salarios'),
]
