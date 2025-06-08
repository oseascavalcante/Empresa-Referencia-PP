from django.contrib import admin
from .models import Equipe, ComposicaoEquipe, EscopoAtividade

@admin.register(EscopoAtividade)
class EscopoAtividadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nome',)

