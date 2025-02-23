from django.urls import path
from .views import ContractCreateView

urlpatterns = [
    path('contracts/new/', ContractCreateView.as_view(), name='contract_create'),
]