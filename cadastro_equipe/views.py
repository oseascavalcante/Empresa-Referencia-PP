from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import Equipe, Funcao, ComposicaoEquipe
from .forms import EquipeForm, FuncaoForm
from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from cad_contrato.models import ContractConfiguration


class EquipeCreateView(CreateView):
    model = Equipe
    form_class = EquipeForm
    template_name = 'adicionar_equipe.html'
    success_url = reverse_lazy('adicionar_equipe')


class FuncaoCreateView(CreateView):
    model = Funcao
    form_class = FuncaoForm
    template_name = 'adicionar_funcao.html'
    success_url = reverse_lazy('adicionar_funcao')

class ComposicaoEquipeView(View):
    def get(self, request, contrato_id):
        contrato = get_object_or_404(ContractConfiguration, contrato=contrato_id)
        equipes = Equipe.objects.all()
        funcoes = Funcao.objects.all()
        composicoes = ComposicaoEquipe.objects.filter(contrato=contrato)
        
        return render(request, 'composicao_equipe.html', {
            'contrato_id': contrato_id,
            'equipes': equipes,
            'funcoes': funcoes,
            'composicoes': composicoes,
        })

    def post(self, request, contrato_id):  # Adicione o argumento contrato_id aqui
        data = json.loads(request.body)
        equipe_id = data.get('equipe_id')

        if not contrato_id or not equipe_id:
            return JsonResponse({'status': 'error', 'message': 'Contrato ID ou Equipe ID não fornecido'}, status=400)

        contrato = get_object_or_404(ContractConfiguration, contrato=contrato_id)
        equipe = get_object_or_404(Equipe, id=equipe_id)

        for row in data['dados']:
            try:
                funcao = Funcao.objects.get(nome=row[0])
            except Funcao.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f'Função {row[0]} não encontrada'}, status=400)
            
            ComposicaoEquipe.objects.create(
                contrato=contrato,
                equipe=equipe,
                quantidade_equipes=data['quantidade_equipes'],
                funcao=funcao,
                quantidade_funcionarios=row[1],
                periculosidade=row[3],
                horas_extras_50=row[4],
                horas_extras_70=row[5],
                horas_extras_100=row[6],
                horas_sobreaviso=row[7],
                horas_adicional_noturno=row[8],
                outros_custos=row[9]
            )

        return JsonResponse({'status': 'success'})