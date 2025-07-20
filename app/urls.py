from django.contrib import admin
from django.urls import path, include
from .views import home, menu_cadastro_estrutura


urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", home, name="home"),
    path('menu_cadastro_estrutura/', menu_cadastro_estrutura, name='menu_cadastro_estrutura'),
    path('cad_contrato/', include('cad_contrato.urls')),
    path('cadastro_equipe/', include('cadastro_equipe.urls')),
    path('mao_obra/', include('mao_obra.urls')),
    path('custo_direto/', include('custo_direto.urls')),
]

