from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.urls import reverse
from .forms import GrupoAEncargosForm, GrupoBIndenizacoesForm, GrupoCSubstituicoesForm
from .models import GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes
from cadastro_equipe.models import FuncaoEquipe

class GrupoABCFormView(View):
    template_name = 'grupo_abc_form.html'

    def get(self, request, composicao_id):
        composicao = get_object_or_404(FuncaoEquipe, id=composicao_id)
        form_a = GrupoAEncargosForm(instance=GrupoAEncargos.objects.filter(composicao=composicao).first())
        form_b = GrupoBIndenizacoesForm(instance=GrupoBIndenizacoes.objects.filter(composicao=composicao).first())
        form_c = GrupoCSubstituicoesForm(instance=GrupoCSubstituicoes.objects.filter(composicao=composicao).first())

        return render(request, self.template_name, {'form_a': form_a, 'form_b': form_b, 'form_c': form_c, 'composicao': composicao})

    def post(self, request, composicao_id):
        composicao = get_object_or_404(FuncaoEquipe, id=composicao_id)
        form_a = GrupoAEncargosForm(request.POST, instance=GrupoAEncargos.objects.filter(composicao=composicao).first())
        form_b = GrupoBIndenizacoesForm(request.POST, instance=GrupoBIndenizacoes.objects.filter(composicao=composicao).first())
        form_c = GrupoCSubstituicoesForm(request.POST, instance=GrupoCSubstituicoes.objects.filter(composicao=composicao).first())

        if form_a.is_valid() and form_b.is_valid() and form_c.is_valid():
            grupo_a = form_a.save(commit=False)
            grupo_a.composicao = composicao
            grupo_a.save()

            grupo_b = form_b.save(commit=False)
            grupo_b.composicao = composicao
            grupo_b.save()

            grupo_c = form_c.save(commit=False)
            grupo_c.composicao = composicao
            grupo_c.save()

            return redirect(reverse('grupo_abc_form', kwargs={'composicao_id': composicao_id}))
        return render(request, self.template_name, {'form_a': form_a, 'form_b': form_b, 'form_c': form_c, 'composicao': composicao})
