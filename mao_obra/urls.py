from django.urls import path
from .views import GrupoABCFormView, GrupoResultadosView, BeneficiosColaboradorUpdateView

urlpatterns = [
    path('grupo_abc_form/<int:contrato_id>/', GrupoABCFormView.as_view(), name='grupo_abc_form'),
    path('grupo_abc_resultados/<int:contrato_id>/', GrupoResultadosView.as_view(), name='grupo_abc_resultados'),
    path('beneficios/<int:contrato_id>/', BeneficiosColaboradorUpdateView.as_view(), name='editar_beneficios'),
   
]