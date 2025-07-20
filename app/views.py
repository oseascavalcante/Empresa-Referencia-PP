from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def menu_cadastro_estrutura(request):
    return render(request, 'menu_cadastro_estrutura.html')

