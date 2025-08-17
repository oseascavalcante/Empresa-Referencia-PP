"""
Sistema extensível de checkers para verificar status de formulários.
Cada checker verifica se um formulário específico está completo, parcial ou vazio.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional
from django.db.models import Count, Q


class FormStatus(Enum):
    """Status possíveis para um formulário"""
    VAZIO = 'vazio'          # Nenhum dado cadastrado
    PARCIAL = 'parcial'      # Alguns dados, mas incompleto
    COMPLETO = 'completo'    # Todos os dados necessários preenchidos
    NAO_APLICAVEL = 'na'     # Não se aplica ao contrato atual


class BaseFormChecker(ABC):
    """
    Classe base para todos os checkers de formulário.
    Define a interface que todos os checkers devem implementar.
    """
    
    @abstractmethod
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        """
        Verifica o status de preenchimento do formulário.
        
        Args:
            contrato_id (int): ID do contrato a ser verificado
            
        Returns:
            dict: {
                'status': FormStatus,
                'count': int,           # Quantidade de itens cadastrados
                'required_count': int,  # Quantidade mínima necessária (opcional)
                'details': dict,        # Detalhes adicionais (opcional)
                'message': str          # Mensagem descritiva
            }
        """
        pass
    
    def get_form_id(self) -> str:
        """Retorna o ID único do formulário"""
        return self.__class__.__name__.lower().replace('checker', '')


class RegionaisChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de regionais"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from cad_contrato.models import Regional
        
        count = Regional.objects.filter(contrato_id=contrato_id).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhuma regional cadastrada"
        elif count >= 1:
            status = FormStatus.COMPLETO
            message = f"{count} regional(is) cadastrada(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 1,
            'message': message,
            'details': {'regionais_count': count}
        }


class EquipesChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de equipes"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from cadastro_equipe.models import Equipe
        
        count = Equipe.objects.filter(contrato_id=contrato_id).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhuma equipe cadastrada"
        elif count >= 1:
            status = FormStatus.COMPLETO
            message = f"{count} equipe(s) cadastrada(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 1,
            'message': message,
            'details': {'equipes_count': count}
        }


class FuncoesChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de funções"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from cadastro_equipe.models import Funcao
        
        # Verifica funções com salário preenchido
        funcoes_completas = Funcao.objects.filter(
            contrato_id=contrato_id,
            salario__gt=0
        ).count()
        
        funcoes_total = Funcao.objects.filter(contrato_id=contrato_id).count()
        
        if funcoes_total == 0:
            status = FormStatus.VAZIO
            message = "Nenhuma função cadastrada"
        elif funcoes_completas == 0:
            status = FormStatus.PARCIAL
            message = f"{funcoes_total} função(ões) sem salário"
        elif funcoes_completas == funcoes_total:
            status = FormStatus.COMPLETO
            message = f"{funcoes_completas} função(ões) completa(s)"
        else:
            status = FormStatus.PARCIAL
            message = f"{funcoes_completas}/{funcoes_total} com salário"
        
        return {
            'status': status,
            'count': funcoes_completas,
            'required_count': 1,
            'message': message,
            'details': {
                'funcoes_completas': funcoes_completas,
                'funcoes_total': funcoes_total
            }
        }


class EscoposChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de escopos"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from cadastro_equipe.models import EscopoAtividade
        
        count = EscopoAtividade.objects.filter(contrato_id=contrato_id).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhum escopo cadastrado"
        elif count >= 1:
            status = FormStatus.COMPLETO
            message = f"{count} escopo(s) cadastrado(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 1,
            'message': message,
            'details': {'escopos_count': count}
        }


class EPIChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de EPI"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoVidaUtil
        
        count = EquipamentoVidaUtil.objects.filter(
            contrato_id=contrato_id,
            categoria='EPI'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhum EPI cadastrado"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} EPI(s) cadastrado(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,  # Não obrigatório
            'message': message,
            'details': {'epi_count': count}
        }


class EPCChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de EPC"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoVidaUtil
        
        count = EquipamentoVidaUtil.objects.filter(
            contrato_id=contrato_id,
            categoria='EPC'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhum EPC cadastrado"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} EPC(s) cadastrado(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'epc_count': count}
        }


class FerramentasChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de ferramentas"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoVidaUtil
        
        count = EquipamentoVidaUtil.objects.filter(
            contrato_id=contrato_id,
            categoria='FERRAMENTAS'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhuma ferramenta cadastrada"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} ferramenta(s) cadastrada(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'ferramentas_count': count}
        }


class EquipamentosTIChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de equipamentos TI"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoVidaUtil
        
        count = EquipamentoVidaUtil.objects.filter(
            contrato_id=contrato_id,
            categoria='EQUIPAMENTOS_TI'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhum equipamento TI cadastrado"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} equipamento(s) TI cadastrado(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'equipamentos_ti_count': count}
        }


class DespesasTIChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de despesas TI"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoMensal
        
        count = EquipamentoMensal.objects.filter(
            contrato_id=contrato_id,
            categoria='DESPESAS_TI'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhuma despesa TI cadastrada"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} despesa(s) TI cadastrada(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'despesas_ti_count': count}
        }


class MateriaisConsumoChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de materiais de consumo"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoMensal
        
        count = EquipamentoMensal.objects.filter(
            contrato_id=contrato_id,
            categoria='MATERIAIS_CONSUMO'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhum material cadastrado"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} material(is) cadastrado(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'materiais_count': count}
        }


class DespesasDiversasChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de despesas diversas"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        from equipamentos.models import EquipamentoMensal
        
        count = EquipamentoMensal.objects.filter(
            contrato_id=contrato_id,
            categoria='DESPESAS_DIVERSAS'
        ).count()
        
        if count == 0:
            status = FormStatus.VAZIO
            message = "Nenhuma despesa diversa cadastrada"
        else:
            status = FormStatus.COMPLETO
            message = f"{count} despesa(s) diversa(s) cadastrada(s)"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'despesas_diversas_count': count}
        }


class CadastrarVeiculosChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de veículos"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        # Implementação fictícia - retorna sempre vazio por enquanto
        # No futuro, isso verificará o modelo de veículos
        count = 0
        
        status = FormStatus.VAZIO
        message = "Nenhum veículo cadastrado"
        
        return {
            'status': status,
            'count': count,
            'required_count': 1,
            'message': message,
            'details': {'veiculos_count': count}
        }


class AtribuirVeiculosChecker(BaseFormChecker):
    """Checker para verificar status de atribuição de veículos"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        # Implementação fictícia - retorna sempre vazio por enquanto  
        # No futuro, isso verificará atribuições de veículos às equipes
        count = 0
        
        status = FormStatus.VAZIO
        message = "Nenhuma atribuição de veículo configurada"
        
        return {
            'status': status,
            'count': count,
            'required_count': 0,
            'message': message,
            'details': {'atribuicoes_veiculos_count': count}
        }


class EncargosAssignacionChecker(BaseFormChecker):
    """Checker para verificar status dos encargos sociais"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            # Importa modelos de encargos sociais
            from mao_obra.models import GrupoAEncargos, GrupoBIndenizacoes, GrupoCSubstituicoes
            
            # Verifica se existe pelo menos um registro de cada grupo para o contrato
            grupo_a_count = GrupoAEncargos.objects.filter(contrato_id=contrato_id).count()
            grupo_b_count = GrupoBIndenizacoes.objects.filter(contrato_id=contrato_id).count()
            grupo_c_count = GrupoCSubstituicoes.objects.filter(contrato_id=contrato_id).count()
            
            total_count = grupo_a_count + grupo_b_count + grupo_c_count
            
            if total_count == 0:
                status = FormStatus.VAZIO
                message = "Encargos sociais não configurados"
            elif grupo_a_count > 0 and grupo_b_count > 0 and grupo_c_count > 0:
                status = FormStatus.COMPLETO
                message = f"Encargos sociais configurados (A:{grupo_a_count}, B:{grupo_b_count}, C:{grupo_c_count})"
            else:
                status = FormStatus.PARCIAL
                message = f"Configuração parcial (A:{grupo_a_count}, B:{grupo_b_count}, C:{grupo_c_count})"
            
            return {
                'status': status,
                'count': total_count,
                'required_count': 3,  # Pelo menos um de cada grupo
                'message': message,
                'details': {
                    'grupo_a_count': grupo_a_count,
                    'grupo_b_count': grupo_b_count,
                    'grupo_c_count': grupo_c_count,
                    'total_count': total_count
                }
            }
            
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 3,
                'message': f"Erro ao verificar encargos sociais: {str(e)}",
                'details': {'error': str(e)}
            }


class BeneficiosChecker(BaseFormChecker):
    """Checker para verificar status dos benefícios dos colaboradores"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            from mao_obra.models import BeneficiosColaborador
            
            # Verifica se existe registro de benefícios para o contrato
            try:
                beneficios = BeneficiosColaborador.objects.get(contrato_id=contrato_id)
                
                # Lista de campos de benefícios para verificar preenchimento
                campos_beneficios = [
                    'transporte', 'cesta_basica', 'refeicao', 'exames_periodicos',
                    'assistencia_medica_odonto', 'seguro_vida', 'previdencia_privada',
                    'alojamento', 'outros_custos'
                ]
                
                # Conta quantos campos estão preenchidos (valores > 0)
                campos_preenchidos = 0
                for campo in campos_beneficios:
                    try:
                        valor = getattr(beneficios, campo, 0)
                        if valor and float(valor) > 0:
                            campos_preenchidos += 1
                    except (ValueError, TypeError):
                        continue
                
                # Determina o status baseado no preenchimento
                if campos_preenchidos == 0:
                    status = FormStatus.VAZIO
                    message = "Nenhum benefício configurado"
                elif campos_preenchidos >= 3:  # Considera adequado se pelo menos 3 benefícios estão configurados
                    status = FormStatus.COMPLETO
                    message = f"{campos_preenchidos} benefício(s) configurado(s)"
                else:
                    status = FormStatus.PARCIAL
                    message = f"{campos_preenchidos} benefício(s) configurado(s) - considere adicionar mais"
                
                # Calcula o total manualmente pois o campo total foi removido do modelo
                try:
                    total_valor = sum([
                        float(getattr(beneficios, campo, 0) or 0)
                        for campo in campos_beneficios
                    ])
                except (ValueError, TypeError):
                    total_valor = 0
                
                return {
                    'status': status,
                    'count': campos_preenchidos,
                    'required_count': 1,  # Reduzido de 3 para 1
                    'message': message,
                    'details': {
                        'beneficios_configurados': campos_preenchidos,
                        'total_beneficios': len(campos_beneficios),
                        'total_valor': total_valor
                    }
                }
                
            except BeneficiosColaborador.DoesNotExist:
                return {
                    'status': FormStatus.VAZIO,
                    'count': 0,
                    'required_count': 1,
                    'message': "Benefícios não configurados",
                    'details': {'beneficios_configurados': 0}
                }
                
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 1,
                'message': f"Erro ao verificar benefícios: {str(e)}",
                'details': {'error': str(e)}
            }


class ComposicaoEquipesChecker(BaseFormChecker):
    """Checker para verificar status da composição de equipes"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            from cadastro_equipe.models import ComposicaoEquipe, FuncaoEquipe
            
            # Verifica quantas composições de equipe existem para o contrato
            composicoes_count = ComposicaoEquipe.objects.filter(contrato_id=contrato_id).count()
            
            # Verifica quantas funções foram associadas às equipes
            funcoes_associadas_count = FuncaoEquipe.objects.filter(
                contrato_id=contrato_id,
                quantidade_funcionarios__gt=0
            ).count()
            
            # Calcula total de funcionários nas equipes
            total_funcionarios = FuncaoEquipe.objects.filter(
                contrato_id=contrato_id
            ).aggregate(
                total=Count('quantidade_funcionarios')
            )['total'] or 0
            
            # Determina o status baseado nos dados
            if composicoes_count == 0:
                status = FormStatus.VAZIO
                message = "Nenhuma equipe inserida"
            elif funcoes_associadas_count == 0:
                status = FormStatus.PARCIAL
                message = f"{composicoes_count} equipe(s) sem funções definidas"
            elif composicoes_count >= 1 and funcoes_associadas_count >= 1:
                status = FormStatus.COMPLETO
                message = f"{composicoes_count} equipe(s) com {funcoes_associadas_count} função(ões)"
            else:
                status = FormStatus.PARCIAL
                message = f"{composicoes_count} equipe(s) parcialmente configurada(s)"
            
            return {
                'status': status,
                'count': composicoes_count,
                'required_count': 1,
                'message': message,
                'details': {
                    'composicoes_count': composicoes_count,
                    'funcoes_associadas_count': funcoes_associadas_count,
                    'total_funcionarios': total_funcionarios
                }
            }
            
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 1,
                'message': f"Erro ao verificar composição de equipes: {str(e)}",
                'details': {'error': str(e)}
            }


class TiposVeiculosChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de tipos de veículos"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            from veiculos.models import TipoVeiculo
            
            # Tipos de veículos são master data, não específicos por contrato
            count = TipoVeiculo.objects.count()
            
            if count == 0:
                status = FormStatus.VAZIO
                message = "Nenhum tipo de veículo cadastrado"
            elif count >= 1:
                status = FormStatus.COMPLETO
                message = f"{count} tipo(s) de veículo cadastrado(s)"
            
            return {
                'status': status,
                'count': count,
                'required_count': 1,
                'message': message,
                'details': {'tipos_veiculos_count': count}
            }
            
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 1,
                'message': f"Erro ao verificar tipos de veículos: {str(e)}",
                'details': {'error': str(e)}
            }


class PrecosCombustivelChecker(BaseFormChecker):
    """Checker para verificar status dos preços de combustível"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            from veiculos.models import PrecoCombustivel
            
            count = PrecoCombustivel.objects.filter(contrato_id=contrato_id).count()
            
            if count == 0:
                status = FormStatus.VAZIO
                message = "Nenhum preço de combustível configurado"
            elif count >= 2:  # Pelo menos 2 tipos de combustível configurados
                status = FormStatus.COMPLETO
                message = f"{count} preço(s) de combustível configurado(s)"
            else:
                status = FormStatus.PARCIAL
                message = f"{count} preço(s) configurado(s) - configure mais tipos"
            
            return {
                'status': status,
                'count': count,
                'required_count': 1,
                'message': message,
                'details': {'precos_combustivel_count': count}
            }
            
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 1,
                'message': f"Erro ao verificar preços de combustível: {str(e)}",
                'details': {'error': str(e)}
            }


class CadastrarVeiculosChecker(BaseFormChecker):
    """Checker para verificar status do cadastro de veículos"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            from veiculos.models import Veiculo
            
            veiculos_count = Veiculo.objects.filter(contrato_id=contrato_id).count()
            
            # Verifica se há veículos com custos calculados corretamente
            veiculos_completos = 0
            for veiculo in Veiculo.objects.filter(contrato_id=contrato_id):
                try:
                    if (veiculo.valor_aquisicao > 0 and 
                        veiculo.vida_util_meses > 0 and 
                        veiculo.eficiencia_km_litro > 0):
                        veiculos_completos += 1
                except:
                    continue
            
            if veiculos_count == 0:
                status = FormStatus.VAZIO
                message = "Nenhum veículo cadastrado"
            elif veiculos_completos == veiculos_count and veiculos_count >= 1:
                status = FormStatus.COMPLETO
                message = f"{veiculos_count} veículo(s) cadastrado(s)"
            elif veiculos_completos > 0:
                status = FormStatus.PARCIAL
                message = f"{veiculos_completos}/{veiculos_count} veículo(s) completo(s)"
            else:
                status = FormStatus.PARCIAL
                message = f"{veiculos_count} veículo(s) com dados incompletos"
            
            return {
                'status': status,
                'count': veiculos_completos,
                'required_count': 1,
                'message': message,
                'details': {
                    'veiculos_count': veiculos_count,
                    'veiculos_completos': veiculos_completos
                }
            }
            
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 1,
                'message': f"Erro ao verificar veículos: {str(e)}",
                'details': {'error': str(e)}
            }


class AtribuirVeiculosChecker(BaseFormChecker):
    """Checker para verificar status da atribuição de veículos"""
    
    def verificar_status(self, contrato_id: int) -> Dict[str, Any]:
        try:
            from veiculos.models import AtribuicaoVeiculo
            
            atribuicoes_count = AtribuicaoVeiculo.objects.filter(contrato_id=contrato_id).count()
            
            # Calcula quantidade total de veículos atribuídos
            total_quantidade = 0
            for atribuicao in AtribuicaoVeiculo.objects.filter(contrato_id=contrato_id):
                try:
                    total_quantidade += float(atribuicao.quantidade or 0)
                except:
                    continue
            
            if atribuicoes_count == 0:
                status = FormStatus.VAZIO
                message = "Nenhuma atribuição de veículo realizada"
            elif total_quantidade > 0:
                status = FormStatus.COMPLETO
                message = f"{atribuicoes_count} atribuição(ões) - {total_quantidade:.1f} veículos atribuídos"
            else:
                status = FormStatus.PARCIAL
                message = f"{atribuicoes_count} atribuição(ões) sem quantidade definida"
            
            return {
                'status': status,
                'count': atribuicoes_count,
                'required_count': 0,  # Opcional
                'message': message,
                'details': {
                    'atribuicoes_count': atribuicoes_count,
                    'total_quantidade': total_quantidade
                }
            }
            
        except Exception as e:
            return {
                'status': FormStatus.VAZIO,
                'count': 0,
                'required_count': 0,
                'message': f"Erro ao verificar atribuições de veículos: {str(e)}",
                'details': {'error': str(e)}
            }


class FormCheckerFactory:
    """
    Factory para criar checkers dinamicamente.
    Permite registrar novos checkers facilmente.
    """
    
    _checkers = {
        'regionais': RegionaisChecker,
        'equipes': EquipesChecker,
        'funcoes': FuncoesChecker,
        'escopos': EscoposChecker,
        'inserir_equipes': ComposicaoEquipesChecker,
        'composicao_equipes': ComposicaoEquipesChecker,
        'epi': EPIChecker,
        'epc': EPCChecker,
        'ferramentas': FerramentasChecker,
        'equipamentos_ti': EquipamentosTIChecker,
        'despesas_ti': DespesasTIChecker,
        'materiais_consumo': MateriaisConsumoChecker,
        'despesas_diversas': DespesasDiversasChecker,
        'tipos_veiculos': TiposVeiculosChecker,
        'precos_combustivel': PrecosCombustivelChecker,
        'cadastrar_veiculos': CadastrarVeiculosChecker,
        'atribuir_veiculos': AtribuirVeiculosChecker,
        'encargos_sociais': EncargosAssignacionChecker,
        'beneficios': BeneficiosChecker,
    }
    
    @classmethod
    def register_checker(cls, form_id: str, checker_class: BaseFormChecker):
        """Registra um novo checker"""
        cls._checkers[form_id] = checker_class
    
    @classmethod
    def create_checker(cls, form_id: str) -> Optional[BaseFormChecker]:
        """Cria uma instância do checker para o formulário especificado"""
        checker_class = cls._checkers.get(form_id)
        if checker_class:
            return checker_class()
        return None
    
    @classmethod
    def get_available_checkers(cls) -> Dict[str, BaseFormChecker]:
        """Retorna todos os checkers disponíveis"""
        return cls._checkers.copy()
    
    @classmethod
    def has_checker(cls, form_id: str) -> bool:
        """Verifica se existe um checker para o formulário"""
        return form_id in cls._checkers