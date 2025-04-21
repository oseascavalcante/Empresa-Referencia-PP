from django.shortcuts import redirect

def contrato_obrigatorio(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("contrato_id"):
            return redirect(f"/cad_contrato/selecionar/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
