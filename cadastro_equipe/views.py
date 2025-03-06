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
from django.db.models import Sum


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
            'escopo_contrato': contrato.escopo_contrato,
            'funcoes': funcoes,
            'composicoes': composicoes,
        })

    def post(self, request, contrato_id):
        try:
            data = json.loads(request.body)

            equipe_id = data.get('equipe_id')
            quantidade_equipes = data.get('quantidade_equipes')
            dados = data.get('dados')

            if not contrato_id or not equipe_id or not dados:
                return JsonResponse({'status': 'error', 'message': 'Campos obrigatórios ausentes'}, status=400)

            contrato = get_object_or_404(ContractConfiguration, contrato=contrato_id)
            equipe = get_object_or_404(Equipe, id=equipe_id)

            for row in dados:
                funcao_nome = row['funcao'].strip()  # Remove espaços em branco
                
                # 🛑 Ignora linhas vazias
                if not funcao_nome:
                    print("⚠️ Linha ignorada: função vazia")
                    continue

                try:
                    funcao = Funcao.objects.get(nome=funcao_nome)
                except Funcao.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Função {funcao_nome} não encontrada'}, status=400)

                ComposicaoEquipe.objects.create(
                    contrato=contrato,
                    equipe=equipe,
                    quantidade_equipes=quantidade_equipes,
                    funcao=funcao,
                    quantidade_funcionarios=row['quantidade'] or 0,
                    periculosidade=row['periculosidade'] if isinstance(row['periculosidade'], bool) else False,
                    horas_extras_50=row['horas_extras_50'] or 0,
                    horas_extras_70=row['horas_extras_70'] or 0,
                    horas_extras_100=row['horas_extras_100'] or 0,
                    horas_sobreaviso=row['horas_sobreaviso'] or 0,
                    horas_adicional_noturno=row['horas_adicional_noturno'] or 0,
                    outros_custos=row['outros_custos'] or 0.00
                )

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Erro ao decodificar JSON'}, status=400)

        except Exception as e:
            print("❌ Erro inesperado:", str(e))
            return JsonResponse({'status': 'error', 'message': f'Erro interno do servidor: {str(e)}'}, status=500)