from django.contrib import admin
from .models import CadastroContrato, Regional

@admin.register(Regional)
class RegionalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'municipio', 'contrato')
    list_filter = ('contrato',)
    search_fields = ('nome', 'municipio')
