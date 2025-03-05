from django.contrib import admin
from django.urls import path, include
from .views import home


urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", home, name="home"),
    path('cad_contrato/', include('cad_contrato.urls')),
    path('cadastro_equipe/', include('cadastro_equipe.urls')),
]

