# services/cadastro_contrato_service.py

from cad_contrato.models import CadastroContrato
from cadastro_equipe.models import FuncaoEquipe
from mao_obra.models import (
    GrupoAEncargos,
    GrupoBIndenizacoes,
    GrupoCSubstituicoes
)
from custo_direto.models import (
    CustoDireto,
    CustoDiretoFuncao
)

class CadastroContratoService:
    @staticmethod
    def inicializar_contrato(contrato: CadastroContrato):
        """
        Inicializa os registros básicos necessários para o contrato informado:
        - Grupo A Encargos
        - Grupo B Indenizações
        - Grupo C Substituições
        - Custo Direto
        Observação:
        As funções específicas de custo direto (CustoDiretoFuncao) devem ser criadas posteriormente,
        conforme a definição das funções da equipe no contrato.
        """
        # Inicializa os Grupos A, B e C
        GrupoAEncargos.objects.create(
            contrato=contrato
        )

        GrupoBIndenizacoes.objects.create(
            contrato=contrato
        )

        GrupoCSubstituicoes.objects.create(
            contrato=contrato
        )

        # Inicializa o Custo Direto (registro principal vazio)
        CustoDireto.objects.create(
            contrato=contrato
        )
        # Inicializa o Custo Direto (registro principal vazio)
        custo_direto, created = CustoDireto.objects.get_or_create(contrato=contrato)

        # Inicializa os registros de CustoDiretoFuncao para cada FuncaoEquipe associada ao contrato
        for funcao_equipe in FuncaoEquipe.objects.filter(contrato=contrato):
            CustoDiretoFuncao.objects.create(
                contrato=contrato,
                funcao_equipe=funcao_equipe,
                quantidade_funcionarios=funcao_equipe.quantidade_funcionarios,
                funcao_equipe_id=funcao_equipe.funcao_id  # Atribuir explicitamente o ID da função
            )