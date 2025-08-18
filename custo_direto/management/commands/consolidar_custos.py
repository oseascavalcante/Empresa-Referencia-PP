from django.core.management.base import BaseCommand
from django.db import transaction
from cad_contrato.models import CadastroContrato
from custo_direto.services_consolidacao.consolidacao_service import ConsolidacaoService
from custo_direto.models import ConsolidacaoCustoContrato


class Command(BaseCommand):
    help = 'Executa consolidação completa de custos diretos com veículos e equipamentos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contrato-id',
            type=int,
            help='Consolidar apenas para um contrato específico',
        )
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Força recálculo ignorando cache',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular a consolidação sem salvar no banco de dados',
        )
        parser.add_argument(
            '--incremental',
            action='store_true',
            help='Executa consolidação incremental (apenas contratos modificados)',
        )
        parser.add_argument(
            '--regionais',
            action='store_true',
            help='Inclui consolidação por regionais',
        )

    def handle(self, *args, **options):
        contrato_id = options.get('contrato_id')
        force_refresh = options.get('force_refresh')
        dry_run = options.get('dry_run')
        incremental = options.get('incremental')
        incluir_regionais = options.get('regionais')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('MODO SIMULACAO - Nenhum dado sera alterado')
            )

        # Definir contratos a processar
        if contrato_id:
            try:
                contratos = [CadastroContrato.objects.get(contrato=contrato_id)]
                self.stdout.write(f'Processando contrato: {contrato_id}')
            except CadastroContrato.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Contrato {contrato_id} nao encontrado')
                )
                return
        else:
            contratos = CadastroContrato.objects.all()
            self.stdout.write('Processando todos os contratos')

        self.stdout.write(f'[INFO] Total de contratos: {len(contratos)}')
        
        sucessos = 0
        erros = 0
        skipped = 0

        for i, contrato in enumerate(contratos, 1):
            try:
                self.stdout.write(f'\n[{i}/{len(contratos)}] Processando contrato {contrato.contrato}...')
                
                if incremental:
                    # Consolidação incremental
                    if not dry_run:
                        consolidacao = ConsolidacaoService.recalcular_tudo_incremental(contrato.contrato)
                        if consolidacao:
                            self.stdout.write('Consolidacao incremental executada')
                        else:
                            self.stdout.write('Sem mudancas detectadas')
                            skipped += 1
                            continue
                else:
                    # Consolidação completa
                    if not dry_run:
                        with transaction.atomic():
                            # Consolidação do contrato
                            consolidacao = ConsolidacaoService.consolidar_contrato(
                                contrato.contrato, 
                                force_refresh=force_refresh
                            )
                            
                            # Consolidação por regionais se solicitado
                            if incluir_regionais:
                                regionais = ConsolidacaoService.consolidar_todas_regionais(
                                    contrato.contrato,
                                    force_refresh=force_refresh
                                )
                                self.stdout.write(f'   Consolidadas {len(regionais)} regionais')
                
                # Exibir resumo da consolidação
                if not dry_run:
                    self._exibir_resumo_consolidacao(consolidacao)
                
                self.stdout.write('Consolidacao concluida com sucesso')
                sucessos += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao processar contrato {contrato.contrato}: {e}')
                )
                erros += 1

        # Resumo final
        self.stdout.write('\n' + '='*80)
        self.stdout.write(f'RESUMO DA CONSOLIDACAO:')
        self.stdout.write(f'   Sucessos: {sucessos}')
        self.stdout.write(f'   Erros: {erros}')
        self.stdout.write(f'   Ignorados (sem mudancas): {skipped}')
        self.stdout.write(f'   Total: {len(contratos)}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nSimulacao concluida. Para aplicar, execute sem --dry-run')
            )
        else:
            if sucessos > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\nConsolidacao concluida! {sucessos} contratos processados.')
                )
            
            # Estatísticas de cache se disponível
            try:
                from django.core.cache import cache
                cache_stats = cache._cache.get_stats()
                if cache_stats:
                    self.stdout.write(f'\nCache hits: {cache_stats[0].get("get_hits", 0)}')
                    self.stdout.write(f'Cache misses: {cache_stats[0].get("get_misses", 0)}')
            except:
                pass
    
    def _exibir_resumo_consolidacao(self, consolidacao):
        """Exibe resumo detalhado da consolidação."""
        try:
            self.stdout.write('   Resumo de Custos:')
            self.stdout.write(f'      Mao de Obra: R$ {consolidacao.custo_mao_obra:,.2f}')
            self.stdout.write(f'      Veiculos: R$ {consolidacao.custo_veiculos:,.2f}')
            self.stdout.write(f'      Combustivel: R$ {consolidacao.custo_combustivel:,.2f}')
            self.stdout.write(f'      Equipamentos: R$ {consolidacao.custo_equipamentos:,.2f}')
            self.stdout.write(f'      TOTAL: R$ {consolidacao.custo_total:,.2f}')
            
            self.stdout.write('   Recursos:')
            self.stdout.write(f'      Funcionarios: {consolidacao.total_funcionarios:,}')
            self.stdout.write(f'      Equipes: {consolidacao.total_equipes:,.1f}')
            self.stdout.write(f'      Veiculos: {consolidacao.total_veiculos:,.1f}')
            
        except Exception as e:
            self.stdout.write(f'   Erro ao exibir resumo: {e}')