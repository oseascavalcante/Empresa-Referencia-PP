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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contrato {self.contrato} - {self.escopo_contrato}"
