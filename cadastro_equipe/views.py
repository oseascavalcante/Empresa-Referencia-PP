from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import IntegrityError
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView, View
from .models import Equipe, Funcao, ComposicaoEquipe, FuncaoEquipe
from .forms import ComposicaoEquipeForm, EquipeForm, FuncaoForm
from django.shortcuts import redirect, render
import json
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from cad_contrato.models import CadastroContrato, Regional
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        contrato_padrao = self.request.session.get('contrato_id')
        if contrato_padrao:
            kwargs['contrato_padrao'] = contrato_padrao
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato_id = self.request.session.get('contrato_id')
        if contrato_id:
            context['contrato'] = CadastroContrato.objects.get(pk=contrato_id)
        return context
 

import logging

logger = logging.getLogger(__name__)

class ComposicaoEquipeUpdateView(UpdateView):
    model = ComposicaoEquipe
    fields = ['escopo', 'equipe', 'quantidade_equipes', 'observacao']
    success_url = reverse_lazy('composicao_equipe')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato = self.object.contrato  # Obtém o contrato da composição atual

        equipes_cadastradas = Equipe.objects.all()
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
    # Exemplo na view:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato_id = self.kwargs.get('contrato_id')
        context['contrato'] = get_object_or_404(CadastroContrato, pk=contrato_id)
        return context
      
    def get(self, request, contrato_id=None):
        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)

        regional_id = request.GET.get('regional_id')
        escopo_id = request.GET.get('escopo_id')

        composicoes = ComposicaoEquipe.objects.filter(contrato=contrato)
        escopos = EscopoAtividade.objects.all()
        equipes = Equipe.objects.all()
        funcoes = Funcao.objects.filter(contrato=contrato)
        regionais = contrato.regionais.all()  # <-- ADICIONADO

        if regional_id and escopo_id:
            equipes_cadastradas = ComposicaoEquipe.objects.filter(
                contrato=contrato,
                regional_id=regional_id,
                escopo_id=escopo_id
            ).values_list('equipe_id', flat=True)
            equipes_disponiveis = equipes.exclude(id__in=equipes_cadastradas)
        else:
            equipes_disponiveis = equipes

        for composicao in composicoes:
            composicao.total_funcionarios = composicao.funcoes.aggregate(
                Sum('quantidade_funcionarios')
            )['quantidade_funcionarios__sum'] or 0

        return render(request, 'composicao_equipe.html', {
            'contrato': contrato,  # <-- ADICIONADO
            'contrato_id': contrato.contrato,
            'escopos': escopos,
            'equipes': equipes_disponiveis,
            'funcoes': funcoes,
            'composicoes': composicoes,
            'escopo_contrato': contrato.escopo_contrato,
            'inicio_vigencia_contrato': contrato.inicio_vigencia_contrato,
            'fim_vigencia_contrato': contrato.fim_vigencia_contrato,
            'regionais': regionais  # <-- ADICIONADO
        })

    def post(self, request, contrato_id):
        try:
            data = json.loads(request.body)
            print("DEBUG payload recebido:", data)

            contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
            regional = get_object_or_404(Regional, id=data.get('regional_id'))
            escopo = get_object_or_404(EscopoAtividade, id=data.get('escopo_id'))
            equipe = get_object_or_404(Equipe, id=data.get('equipe_id'))

            # Conversão segura de datas
            try:
                data_mobilizacao = datetime.strptime(data.get('data_mobilizacao'), '%Y-%m-%d').date()
                data_desmobilizacao = datetime.strptime(data.get('data_desmobilizacao'), '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Formato de data inválido'}, status=400)

            # Prepara dados para o form
            form_data = {
                'contrato': contrato,
                'regional': regional,
                'escopo': escopo,
                'equipe': equipe,
                'quantidade_equipes': data.get('quantidade_equipes'),
                'observacao': data.get('observacao'),
                'data_mobilizacao': data_mobilizacao,
                'data_desmobilizacao': data_desmobilizacao,
            }

            form = ComposicaoEquipeForm(form_data)

            if not form.is_valid():
                print("ERROS DO FORMULÁRIO:", form.errors)
                # Intercepta duplicidade
                all_errors = form.errors.get("__all__")
                if all_errors:
                    return JsonResponse({"status": "error", "message": str(all_errors[0])}, status=400)
                return JsonResponse({"status": "error", "message": "Erro no preenchimento do formulário."}, status=400)


            composicao = form.save()

            # Inserção de funções
            for row in data.get('dados', []):
                funcao_nome = row.get('funcao', '').strip()
                if not funcao_nome:
                    continue

                try:
                    funcao = Funcao.objects.get(nome=funcao_nome)
                except Funcao.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': f'Função {funcao_nome} não encontrada'}, status=400)

                try:
                    salario_str = row.get('salario', '0').replace(',', '.')
                    salario = Decimal(salario_str)
                except InvalidOperation:
                    return JsonResponse({'status': 'error', 'message': f'Salário inválido: {row.get("salario")}'}, status=400)

                FuncaoEquipe.objects.create(
                    contrato=contrato,
                    composicao=composicao,
                    funcao=funcao,
                    quantidade_funcionarios=row.get('quantidade', 0),
                    salario=salario,
                    periculosidade=row.get('periculosidade', False),
                    horas_extras_50=row.get('horas_extras_50', 0),
                    horas_prontidao=row.get('horas_prontidao', 0),
                    horas_extras_100=row.get('horas_extras_100', 0),
                    horas_sobreaviso=row.get('horas_sobreaviso', 0),
                    horas_adicional_noturno=row.get('horas_adicional_noturno', 0),
                    outros_custos=row.get('outros_custos', 0),
                )

            return JsonResponse({'status': 'success'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            print("Erro interno:", str(e))
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

    def get(self, request, contrato_id=None):
        contratos = CadastroContrato.objects.all().order_by("contrato")

        contrato = (
            get_object_or_404(CadastroContrato, contrato=contrato_id)
            if contrato_id else contratos.first()
        )

        abrir_modal = contrato_id is None

        funcoes_queryset = (
            FuncaoEquipe.objects
            .filter(contrato=contrato)
            .select_related('funcao')
            .order_by('funcao_id')
        )

        funcoes_dict = OrderedDict()
        for funcao_equipe in funcoes_queryset:
            if funcao_equipe.funcao_id not in funcoes_dict:
                funcoes_dict[funcao_equipe.funcao_id] = {
                    'id': funcao_equipe.funcao_id,
                    'nome': funcao_equipe.funcao.nome,
                    'salario_atual': str(funcao_equipe.salario)
                }

        return render(request, self.template_name, {
            'contrato': contrato,
            'funcoes': list(funcoes_dict.values()),
            'contratos': contratos,
            'abrir_modal': abrir_modal,
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
