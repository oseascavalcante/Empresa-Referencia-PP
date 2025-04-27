from decimal import Decimal, InvalidOperation
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView, View
from .models import Equipe, Funcao, ComposicaoEquipe, FuncaoEquipe
from .forms import EquipeForm, FuncaoForm
from django.shortcuts import redirect, render
import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from cad_contrato.models import CadastroContrato
from django.db.models import Sum
from collections import OrderedDict

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

        # Obter o contrato associado à composição
        contrato = composicao.contrato

        # Atualizar FuncaoEquipe
        FuncaoEquipe.objects.filter(composicao=composicao).delete()
        for row in data.get('dados', []):
            funcao_nome = row['funcao'].strip()
            if not funcao_nome:
                continue

            funcao = get_object_or_404(Funcao, nome=funcao_nome)
            
            salario = row.get('salario', funcao.salario)
            if isinstance(salario, str):
                salario = salario.replace(',', '.')
            try:
                salario = Decimal(salario)
            except InvalidOperation:
                return JsonResponse({'status': 'error', 'message': f'O valor "{salario}" não é um número decimal válido.'}, status=400)
           
            FuncaoEquipe.objects.create(
                contrato=contrato,  # Passar o contrato associado
                composicao=composicao,
                funcao=funcao,
                quantidade_funcionarios=row['quantidade'] or 0,
                salario=row.get('salario', funcao.salario),
                periculosidade=row['periculosidade'] if isinstance(row['periculosidade'], bool) else False,
                horas_extras_50=row['horas_extras_50'] or 0,
                horas_prontidao=row['horas_prontidao'] or 0,
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
    template_name = 'detalhes_equipe.html'
    context_object_name = 'composicao'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['funcoes'] = FuncaoEquipe.objects.filter(composicao=self.object)
        return context

class ComposicaoEquipeView(View):
    def get(self, request, contrato_id=None):
        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
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
            'inicio_vigencia_contrato': contrato.inicio_vigencia_contrato,  # Passa a data no contexto
            'fim_vigencia_contrato': contrato.fim_vigencia_contrato  # Passa a data no contexto
        })

    def post(self, request, contrato_id):
        try:
            data = json.loads(request.body)

            equipe_id = data.get('equipe_id')
            quantidade_equipes = data.get('quantidade_equipes')
            observacao = data.get('observacao')
            dados = data.get('dados')

            contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
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

                # Converte o salário para o formato decimal esperado
                salario = row.get('salario', funcao.salario)
                if isinstance(salario, str):
                    salario = salario.replace(',', '.')
                try:
                    salario = Decimal(salario)
                except InvalidOperation:
                    return JsonResponse({'status': 'error', 'message': f'O valor "{salario}" não é um número decimal válido.'}, status=400)

                FuncaoEquipe.objects.create(
                    contrato=contrato,
                    composicao=composicao,
                    funcao=funcao,
                    quantidade_funcionarios=row['quantidade'] or 0,
                    salario=salario,
                    periculosidade=row['periculosidade'] if isinstance(row['periculosidade'], bool) else False,
                    horas_extras_50=row['horas_extras_50'] or 0,
                    horas_prontidao=row['horas_prontidao'] or 0,
                    horas_extras_100=row['horas_extras_100'] or 0,
                    horas_sobreaviso=row['horas_sobreaviso'] or 0,
                    horas_adicional_noturno=row['horas_adicional_noturno'] or 0,
                    outros_custos=row['outros_custos'] or 0.00
                )

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Erro ao decodificar JSON'}, status=400)

        except Exception as e:
            print("Erro interno:", str(e))  # Log para verificar erros internos
            return JsonResponse({'status': 'error', 'message': f'Erro interno do servidor: {str(e)}'}, status=500)

class ComposicaoEquipeJSONView(View):
    def get(self, request, pk):
        composicao = get_object_or_404(ComposicaoEquipe, pk=pk)
        funcoes = FuncaoEquipe.objects.filter(composicao=composicao)
        
        dados = []
        for funcao in funcoes:
            dados.append({
                'funcao': funcao.funcao.nome,
                'quantidade': funcao.quantidade_funcionarios,
                'salario': str(funcao.salario),
                'periculosidade': funcao.periculosidade,
                'horas_extras_50': funcao.horas_extras_50,
                'horas_prontidao': funcao.horas_prontidao,
                'horas_extras_100': funcao.horas_extras_100,
                'horas_sobreaviso': funcao.horas_sobreaviso,
                'horas_adicional_noturno': funcao.horas_adicional_noturno,
                'outros_custos': funcao.outros_custos,
            })
        
        response_data = {
            'equipe_id': composicao.equipe.id,
            'quantidade_equipes': composicao.quantidade_equipes,
            'data_mobilizacao': composicao.data_mobilizacao.strftime('%d/%m/%Y') if composicao.data_mobilizacao else '',
            'data_desmobilizacao': composicao.data_desmobilizacao.strftime('%d/%m/%Y') if composicao.data_desmobilizacao else '',
            'observacao': composicao.observacao,
            'dados': dados
        }
        return JsonResponse(response_data)


class EditarSalariosView(View):
    template_name = 'editar_salarios.html'

    def get(self, request, contrato_id):
        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)

        # Buscar todas as funções do contrato
        funcoes_queryset = (
            FuncaoEquipe.objects
            .filter(contrato=contrato)
            .select_related('funcao')
            .order_by('funcao_id')  # Facilita o agrupamento
        )

        funcoes_dict = OrderedDict()
        for funcao_equipe in funcoes_queryset:
            if funcao_equipe.funcao_id not in funcoes_dict:
                funcoes_dict[funcao_equipe.funcao_id] = {
                    'id': funcao_equipe.funcao_id,
                    'nome': funcao_equipe.funcao.nome,
                    'salario_atual': str(funcao_equipe.salario)

                }

        funcoes = list(funcoes_dict.values())

        return render(request, self.template_name, {
            'contrato': contrato,
            'funcoes': funcoes
        })

    def post(self, request, contrato_id):
        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
        data = json.loads(request.body)

        for funcao_data in data.get('funcoes', []):
            funcao_id = funcao_data.get('id')
            novo_salario = funcao_data.get('salario')

            if not funcao_id or novo_salario is None:
                continue

            try:
                novo_salario = Decimal(str(novo_salario))
            except InvalidOperation:
                return JsonResponse({'status': 'error', 'message': f'Salário inválido para função ID {funcao_id}.'}, status=400)

            # Atualizar todos os registros dessa função dentro do contrato
            FuncaoEquipe.objects.filter(contrato=contrato, funcao_id=funcao_id).update(salario=novo_salario)

        return JsonResponse({'status': 'success', 'message': 'Salários atualizados com sucesso!'})
