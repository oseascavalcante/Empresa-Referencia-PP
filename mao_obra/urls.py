from django.urls import path
from .views import GrupoABCFormView

urlpatterns = [
    path('grupo_abc_form/<int:composicao_id>/', GrupoABCFormView.as_view(), name='grupo_abc_form'),
]