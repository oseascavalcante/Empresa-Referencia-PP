from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
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
from .models import EscopoAtividade
from .forms import EscopoAtividadeForm

class EscopoAtividadeCreateView(CreateView):
    model = EscopoAtividade
    form_class = EscopoAtividadeForm
    template_name = 'adicionar_escopo.html'
    success_url = reverse_lazy('adicionar_escopo')  # Redireciona para a mesma página após o cadastro    from django.views.generic import CreateView
    from .models import EscopoAtividade
    from django.urls import reverse_lazy
    from .forms import EscopoAtividadeForm
    
    class EscopoAtividadeCreateView(CreateView):
        model = EscopoAtividade
        form_class = EscopoAtividadeForm
        template_name = 'adicionar_escopo.html'
        success_url = reverse_lazy('adicionar_escopo')  # Redireciona para a mesma página após o cadastro

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
 

import logging

logger = logging.getLogger(__name__)

class ComposicaoEquipeUpdateView(UpdateView):
    model = ComposicaoEquipe
    fields = ['escopo', 'equipe', 'quantidade_equipes', 'observacao']
    success_url = reverse_lazy('composicao_equipe')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato = self.object.contrato  # Obtém o contrato da composição atual

        # Filtra as equipes que ainda não foram cadastradas para o contrato
        equipes_cadastradas = ComposicaoEquipe.objects.filter(contrato=contrato).values_list('equipe_id', flat=True)
        context['equipes'] = Equipe.objects.exclude(id__in=equipes_cadastradas)

        # Log para depuração
        logger.info(f"Equipes cadastradas para o contrato {contrato.id}: {list(equipes_cadastradas)}")
        logger.info(f"Equipes disponíveis: {list(context['equipes'])}")

        return context

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "Essa equipe já foi cadastrada para este contrato.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'message': form.errors}, status=400)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        composicao = self.get_object()
    
        composicao.quantidade_equipes = data.get('quantidade_equipes')
        composicao.observacao = data.get('observacao')
        composicao.save()
    
        contrato = composicao.contrato
    
        # Atualizar ou criar registros em FuncaoEquipe
        funcao_ids_atualizados = []
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
    
            # Atualizar ou criar FuncaoEquipe
            funcao_equipe, created = FuncaoEquipe.objects.update_or_create(
                contrato=contrato,
                composicao=composicao,
                funcao=funcao,
                defaults={
                    'quantidade_funcionarios': row['quantidade'] or 0,
                    'salario': salario,
                    'periculosidade': row['periculosidade'] if isinstance(row['periculosidade'], bool) else False,
                    'horas_extras_50': row['horas_extras_50'] or 0,
                    'horas_prontidao': row['horas_prontidao'] or 0,
                    'horas_extras_100': row['horas_extras_100'] or 0,
                    'horas_sobreaviso': row['horas_sobreaviso'] or 0,
                    'horas_adicional_noturno': row['horas_adicional_noturno'] or 0,
                    'outros_custos': row['outros_custos'] or 0.00,
                }
            )
            funcao_ids_atualizados.append(funcao_equipe.id)
    
        # Remover registros de FuncaoEquipe que não foram atualizados
        FuncaoEquipe.objects.filter(composicao=composicao).exclude(id__in=funcao_ids_atualizados).delete()
    
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
        
         # Filtrar equipes que ainda não foram cadastradas para esse contrato
        equipes_cadastradas = ComposicaoEquipe.objects.filter(contrato=contrato).values_list('equipe_id', flat=True)
        equipes = Equipe.objects.exclude(id__in=equipes_cadastradas)
        funcoes = Funcao.objects.all()
        composicoes = ComposicaoEquipe.objects.filter(contrato=contrato)
        escopos = EscopoAtividade.objects.all()  # <-- AQUI
        
        # Soma total de funcionários por composição
        for composicao in composicoes:
            composicao.total_funcionarios = composicao.funcoes.aggregate(Sum('quantidade_funcionarios'))['quantidade_funcionarios__sum'] or 0

        return render(request, 'composicao_equipe.html', {
            'contrato_id': contrato_id,
            'escopos': escopos,  # <-- E AQUI
            'equipes': equipes,
            'escopo_contrato': contrato.escopo_contrato,
            'funcoes': funcoes,
            'composicoes': composicoes,
            'inicio_vigencia_contrato': contrato.inicio_vigencia_contrato,  # Passa a data no contexto
            'fim_vigencia_contrato': contrato.fim_vigencia_contrato  # Passa a data no contexto
        })

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato = self.object.contrato  # Obtém o contrato da composição atual

        # Equipes já cadastradas, exceto a própria equipe da composição sendo editada
        equipes_cadastradas = ComposicaoEquipe.objects.filter(contrato=contrato).exclude(
            pk=self.object.pk
        ).values_list('equipe_id', flat=True)

        context['equipes'] = Equipe.objects.exclude(id__in=equipes_cadastradas)

        logger.info(f"Equipes cadastradas para o contrato {contrato.id}: {list(equipes_cadastradas)}")
        logger.info(f"Equipes disponíveis: {list(context['equipes'])}")

        return context


    def post(self, request, contrato_id):
        try:
            data = json.loads(request.body)
            
            escopo_id = data.get('escopo_id')  # ou 'escopo', dependendo do nome no frontend
            equipe_id = data.get('equipe_id')
            quantidade_equipes = data.get('quantidade_equipes')
            observacao = data.get('observacao')
            dados = data.get('dados')

            contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
            equipe = get_object_or_404(Equipe, id=equipe_id)

            # Verifica se já existe uma composição dessa equipe para o contrato
            if ComposicaoEquipe.objects.filter(contrato=contrato, equipe=equipe).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Essa equipe já está cadastrada para este contrato.'
                }, status=400)

            # Se não existir, cria
            escopo = get_object_or_404(EscopoAtividade, id=escopo_id)
            composicao = ComposicaoEquipe.objects.create(
                contrato=contrato,
                escopo=escopo,
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
            'equipe_nome': composicao.equipe.nome,  # Adicionado aqui
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
