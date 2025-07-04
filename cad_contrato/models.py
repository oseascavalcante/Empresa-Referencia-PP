from django.db import models

# Cadastro dos Contratos
class CadastroContrato(models.Model):
    ESTADOS_CHOICES = [
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    ]
    
    STATUS_CHOICES = [
        ('EM_LICITACAO', 'Em Licitação'),
        ('EM_RENOVACAO', 'Em Renovação'),
        ('ATIVO', 'Ativo'),
        ('ENCERRADO', 'Encerrado'),
    ]

    contrato = models.AutoField(primary_key=True)
    concessionaria = models.CharField(max_length=100, default='Equatorial')
    estado = models.CharField(max_length=2, choices=ESTADOS_CHOICES, default='GO')
    municipio = models.CharField(max_length=100, default='Goiânia')
    escopo_contrato = models.CharField(max_length=255)
    inicio_vigencia_contrato = models.DateField(default='2025-01-01')
    fim_vigencia_contrato = models.DateField(default='2029-01-01')
    versao_base = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='versoes')
    numero_versao = models.IntegerField(default=0)
    descricao_alteracao = models.TextField(blank=True)
    status_contrato = models.CharField(max_length=15, choices=STATUS_CHOICES, default='EM_LICITACAO', verbose_name="Status do Contrato")
    valor_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Valor Inicial do Contrato")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contrato {self.contrato} - {self.escopo_contrato}"

class Regional(models.Model):
    contrato = models.ForeignKey(
        'cad_contrato.CadastroContrato',
        on_delete=models.CASCADE,
        related_name='regionais',
        verbose_name='Contrato'
    )
    nome = models.CharField(max_length=100, verbose_name='Nome da Regional')
    municipio = models.CharField(max_length=100, verbose_name='Município')

    class Meta:
        unique_together = ('contrato', 'nome')
        verbose_name = 'Regional'
        verbose_name_plural = 'Regionais'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.municipio}"
