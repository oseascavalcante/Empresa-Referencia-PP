
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, DetailView
from django.views.generic.edit import UpdateView
from .models import (
    GrupoAEncargos,
    GrupoBIndenizacoes,
    GrupoCSubstituicoes,
    CalcGrupoAEncargos,
    CalcGrupoBIndenizacoes,
    CalcGrupoCSubstituicoes,
    CalcGrupoD,
    CalcGrupoE,
    BeneficiosColaborador,
)
from .forms import (
    GrupoAEncargosForm,
    GrupoBIndenizacoesForm,
    GrupoCSubstituicoesForm,
    BeneficiosColaboradorForm,
)
from .services import GrupoCalculationsService
from cad_contrato.models import CadastroContrato
from cad_contrato.utils import contrato_obrigatorio


@method_decorator(contrato_obrigatorio, name='dispatch')
class GrupoABCFormView(FormView):
    template_name = 'grupo_abc_form.html'
    success_url = 'grupo_abc_resultados'
    form_class = GrupoAEncargosForm

    def dispatch(self, request, *args, **kwargs):
        self.contrato = get_object_or_404(CadastroContrato, contrato=kwargs.get('contrato_id'))
        request.session['contrato_id'] = self.contrato.contrato
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        grupo_a = GrupoAEncargos.objects.filter(contrato=self.contrato).first()
        kwargs['instance'] = grupo_a
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grupo_a = GrupoAEncargos.objects.filter(contrato=self.contrato).first()
        grupo_b = GrupoBIndenizacoes.objects.filter(contrato=self.contrato).first()
        grupo_c = GrupoCSubstituicoes.objects.filter(contrato=self.contrato).first()

        context['form_a'] = GrupoAEncargosForm(instance=grupo_a)
        context['form_b'] = GrupoBIndenizacoesForm(instance=grupo_b)
        context['form_c'] = GrupoCSubstituicoesForm(instance=grupo_c)
        context['contrato'] = self.contrato
        context['contratos'] = CadastroContrato.objects.all()  # 👈 Necessário para o select
        return context

    def post(self, request, *args, **kwargs):
        grupo_a = GrupoAEncargos.objects.filter(contrato=self.contrato).first()
        grupo_b = GrupoBIndenizacoes.objects.filter(contrato=self.contrato).first()
        grupo_c = GrupoCSubstituicoes.objects.filter(contrato=self.contrato).first()

        form_a = GrupoAEncargosForm(request.POST, instance=grupo_a)
        form_b = GrupoBIndenizacoesForm(request.POST, instance=grupo_b)
        form_c = GrupoCSubstituicoesForm(request.POST, instance=grupo_c)

        if form_a.is_valid() and form_b.is_valid() and form_c.is_valid():
            obj_a = form_a.save(commit=False)
            obj_b = form_b.save(commit=False)
            obj_c = form_c.save(commit=False)

            obj_a.contrato = self.contrato
            obj_b.contrato = self.contrato
            obj_c.contrato = self.contrato

            obj_a.save()
            obj_b.save()
            obj_c.save()
            # Chamar o serviço de cálculo
            GrupoCalculationsService.calcular_todos_grupos(self.contrato)
            
            # Redirecionar para a URL com o contrato_id
            return redirect('grupo_abc_resultados', contrato_id=self.contrato.contrato)

        # Se algum formulário não for válido
        context = self.get_context_data()
        context['form_a'] = form_a
        context['form_b'] = form_b
        context['form_c'] = form_c
        return self.render_to_response(context)


class GrupoResultadosView(DetailView):
    template_name = 'grupo_abc_resultados.html'
    context_object_name = 'calc_grupo_a'

    def get_object(self):
        contrato_id = self.kwargs.get('contrato_id')
        self.contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
        return get_object_or_404(CalcGrupoAEncargos, contrato_id=self.contrato.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contrato_id = self.kwargs.get('contrato_id')

        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
        context['contrato'] = contrato
        context['grupo_a'] = GrupoAEncargos.objects.filter(contrato=contrato).first()
        context['calc_grupo_a'] = CalcGrupoAEncargos.objects.filter(contrato=contrato).first()
        context['calc_grupo_b'] = CalcGrupoBIndenizacoes.objects.filter(contrato=contrato).first()
        context['calc_grupo_c'] = CalcGrupoCSubstituicoes.objects.filter(contrato=contrato).first()
        context['calc_grupo_d'] = CalcGrupoD.objects.filter(contrato=contrato).first()
        context['calc_grupo_e'] = CalcGrupoE.objects.filter(contrato=contrato).first()

        return context



class BeneficiosColaboradorUpdateView(View):
    template_name = 'editar_beneficios.html'

    def get(self, request, contrato_id):
        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
        beneficio, _ = BeneficiosColaborador.objects.get_or_create(contrato=contrato)
        form = BeneficiosColaboradorForm(instance=beneficio)
        return render(request, self.template_name, {'form': form, 'contrato': contrato})

    def post(self, request, contrato_id):
        contrato = get_object_or_404(CadastroContrato, contrato=contrato_id)
        beneficio = get_object_or_404(BeneficiosColaborador, contrato=contrato)
        form = BeneficiosColaboradorForm(request.POST, instance=beneficio)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.contrato = contrato  # Força vínculo
            obj.save()
            return redirect(reverse('menu_despesas', kwargs={'contrato_id': contrato_id}))

        return render(request, self.template_name, {'form': form, 'contrato': contrato})
