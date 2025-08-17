from django.core.management.base import BaseCommand
from django.db import transaction
from cadastro_equipe.models import FuncaoEquipe
from custo_direto.services import calcular_custo_funcao
from mao_obra.models import EncargosSociaisCentralizados, BeneficiosColaborador
from mao_obra.services import BeneficioCustoDiretoService


class Command(BaseCommand):
    help = 'Recalcula todos os custos diretos baseados nas funções de equipe existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contrato-id',
            type=int,
            help='Recalcular apenas para um contrato específico',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular o recálculo sem salvar no banco de dados',
        )

    def handle(self, *args, **options):
        contrato_id = options.get('contrato_id')
        dry_run = options.get('dry_run')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO SIMULAÇÃO - Nenhum dado será alterado')
            )

        # Filtrar por contrato se especificado
        funcoes_equipe = FuncaoEquipe.objects.select_related(
            'contrato', 'composicao', 'funcao'
        )
        
        if contrato_id:
            funcoes_equipe = funcoes_equipe.filter(contrato_id=contrato_id)
            self.stdout.write(f'📋 Processando contrato: {contrato_id}')
        else:
            self.stdout.write('📋 Processando todos os contratos')

        funcoes_equipe = funcoes_equipe.filter(quantidade_funcionarios__gt=0)
        
        total_funcoes = funcoes_equipe.count()
        if total_funcoes == 0:
            self.stdout.write(
                self.style.WARNING('[AVISO] Nenhuma função de equipe encontrada com funcionários')
            )
            return

        self.stdout.write(f'[INFO] Total de funções a processar: {total_funcoes}')
        
        sucessos = 0
        erros = 0

        for i, funcao_equipe in enumerate(funcoes_equipe, 1):
            try:
                contrato = funcao_equipe.contrato
                
                # Busca encargos sociais
                encargos = EncargosSociaisCentralizados.objects.filter(
                    contrato=contrato
                ).first()
                
                # Busca e calcula benefícios
                beneficios_valor = 0
                beneficios = BeneficiosColaborador.objects.filter(contrato=contrato).first()
                if beneficios:
                    beneficios_valor = BeneficioCustoDiretoService.calcular_beneficios_por_funcao(
                        contrato=contrato,
                        salario_base_funcao=funcao_equipe.salario
                    )

                if not dry_run:
                    with transaction.atomic():
                        custo_funcao = calcular_custo_funcao(
                            funcao_equipe=funcao_equipe,
                            contrato=contrato,
                            encargos=encargos,
                            beneficios=beneficios_valor
                        )
                        
                self.stdout.write(
                    f'✅ [{i}/{total_funcoes}] {funcao_equipe.funcao.nome} - '
                    f'{funcao_equipe.composicao.equipe.nome} (Contrato {contrato.contrato})'
                )
                sucessos += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'[ERRO] [{i}/{total_funcoes}] Erro ao processar {funcao_equipe}: {e}'
                    )
                )
                erros += 1

        # Resumo final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'[RESUMO] RESUMO DO PROCESSAMENTO:')
        self.stdout.write(f'   [OK] Sucessos: {sucessos}')
        self.stdout.write(f'   [ERRO] Erros: {erros}')
        self.stdout.write(f'   [INFO] Total: {total_funcoes}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n🔍 Simulação concluída. Para aplicar as mudanças, execute sem --dry-run')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Recálculo concluído! {sucessos} custos diretos atualizados.')
            )