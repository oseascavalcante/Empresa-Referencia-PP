from cad_contrato.models import CadastroContrato

def contrato_context(request):
    contrato_id = request.session.get('contrato_id')
    contrato = None
    if contrato_id:
        try:
            contrato = CadastroContrato.objects.get(contrato=contrato_id)
        except CadastroContrato.DoesNotExist:
            pass
    return {'contrato': contrato}