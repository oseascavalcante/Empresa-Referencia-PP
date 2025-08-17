from django.contrib import admin
from django.urls import path, include
from .views import home, menu_cadastro_estrutura


urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", home, name="home"),
    path('menu_cadastro_estrutura/', menu_cadastro_estrutura, name='menu_cadastro_estrutura'),
    path('menu_admin/', menu_cadastro_estrutura, {'filter_category': 'admin'}, name='menu_admin'),
    
    path('cad_contrato/', include('cad_contrato.urls')),
    path('cadastro_equipe/', include('cadastro_equipe.urls')),
    path('mao_obra/', include('mao_obra.urls')),
    path('custo_direto/', include('custo_direto.urls')),
    path('equipamentos/', include('equipamentos.urls')),
    path('veiculos/', include('veiculos.urls')),
]

