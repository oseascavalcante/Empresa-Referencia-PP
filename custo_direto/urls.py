# custo_direto/urls.py

from django.urls import path
from .views import DashboardCustoDiretoView

urlpatterns = [
    path('dashboard/', DashboardCustoDiretoView.as_view(), name='dashboard_custo_direto'),
]
