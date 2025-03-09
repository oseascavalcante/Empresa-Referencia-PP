from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from .models import Equipe, Funcao, ComposicaoEquipe, FuncaoEquipe
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
 

class ComposicaoEquipeUpdateView(UpdateView):
    model = ComposicaoEquipe
    fields = ['quantidade_equipes', 'observacao']
    success_url = reverse_lazy('composicao_equipe')

    def form_valid(self, form):
        response = super().form_valid(form)
        return JsonResponse({'status': 'success'})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'message': form.errors}, status=400)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        composicao = self.get_object()

        composicao.quantidade_equipes = data.get('quantidade_equipes')
        composicao.observacao = data.get('observacao')
        composicao.save()

        # Atualizar FuncaoEquipe
        FuncaoEquipe.objects.filter(composicao=composicao).delete()
        for row in data.get('dados', []):
            funcao_nome = row['funcao'].strip()
            if not funcao_nome:
                continue

            funcao = get_object_or_404(Funcao, nome=funcao_nome)
            FuncaoEquipe.objects.create(
                composicao=composicao,
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

class ComposicaoEquipeDeleteView(DeleteView):
    model = ComposicaoEquipe
    success_url = reverse_lazy('composicao_equipe')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': 'success'})


class ComposicaoEquipeDetailView(DetailView):
    model = ComposicaoEquipe
    template_name = 'detalhes_composicao.html'
    context_object_name = 'composicao'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['funcoes'] = FuncaoEquipe.objects.filter(composicao=self.object)
        return context


class ComposicaoEquipeView(View):
    def get(self, request, contrato_id=None):
        contrato = get_object_or_404(ContractConfiguration, contrato=contrato_id)
        equipes = Equipe.objects.all()
        funcoes = Funcao.objects.all()
        composicoes = ComposicaoEquipe.objects.filter(contrato=contrato)

        # Soma total de funcionários por composição
        for composicao in composicoes:
            composicao.total_funcionarios = composicao.funcoes.aggregate(Sum('quantidade_funcionarios'))['quantidade_funcionarios__sum'] or 0

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
            observacao = data.get('observacao')
            dados = data.get('dados')

            contrato = get_object_or_404(ContractConfiguration, contrato=contrato_id)
            equipe = get_object_or_404(Equipe, id=equipe_id)

            composicao = ComposicaoEquipe.objects.create(
                contrato=contrato,
                equipe=equipe,
                quantidade_equipes=quantidade_equipes,
                observacao=observacao
            )

            for row in dados:
                funcao_nome = row['funcao'].strip()  # Remove espaços em branco
                
                # Ignora linhas vazias
                if not funcao_nome:
                    continue

                try:
                    funcao = Funcao.objects.get(nome=funcao_nome)
                except Funcao.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Função {funcao_nome} não encontrada'}, status=400)

                FuncaoEquipe.objects.create(
                    composicao=composicao,
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
            return JsonResponse({'status': 'error', 'message': f'Erro interno do servidor: {str(e)}'}, status=500)