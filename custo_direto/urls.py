# custo_direto/urls.py

from django.urls import path
from .views import DashboardCustoDiretoView, RecalcularCustosView

urlpatterns = [
    path('dashboard/', DashboardCustoDiretoView.as_view(), name='dashboard_custo_direto'),
    path('recalcular/', RecalcularCustosView.as_view(), name='recalcular_custos'),
]
