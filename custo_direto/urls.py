# custo_direto/urls.py

from django.urls import path
from .views import DashboardCustoDiretoView, RecalcularCustosView
from .views_consolidadas import DashboardConsolidadoView, ConsolidacaoAPIView, RecalcularConsolidacaoView

urlpatterns = [
    path('dashboard/', DashboardCustoDiretoView.as_view(), name='dashboard_custo_direto'),
    path('dashboard-consolidado/', DashboardConsolidadoView.as_view(), name='dashboard_consolidado'),
    path('api/consolidacao/', ConsolidacaoAPIView.as_view(), name='api_consolidacao'),
    path('recalcular-consolidacao/', RecalcularConsolidacaoView.as_view(), name='recalcular_consolidacao'),
    path('recalcular/', RecalcularCustosView.as_view(), name='recalcular_custos'),
]
