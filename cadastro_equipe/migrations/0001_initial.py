# Generated by Django 5.1.6 on 2025-06-08 17:49

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("cad_contrato", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Equipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="EscopoAtividade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nome",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Nome do Escopo"
                    ),
                ),
                (
                    "descricao",
                    models.TextField(
                        blank=True, null=True, verbose_name="Descrição do Escopo"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Funcao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=100, unique=True)),
                (
                    "salario",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ComposicaoEquipe",
            fields=[
                (
                    "composicao_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "quantidade_equipes",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("data_mobilizacao", models.DateField(default="2025-01-01")),
                ("data_desmobilizacao", models.DateField(default="2028-01-01")),
                ("prefixo_equipe", models.TextField(blank=True, null=True)),
                ("observacao", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contrato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cad_contrato.cadastrocontrato",
                    ),
                ),
                (
                    "regional",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="composicoes",
                        to="cad_contrato.regional",
                        verbose_name="Regional",
                    ),
                ),
                (
                    "equipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cadastro_equipe.equipe",
                    ),
                ),
                (
                    "escopo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="composicoes",
                        to="cadastro_equipe.escopoatividade",
                        verbose_name="Escopo da Atividade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Composição de Equipe",
                "verbose_name_plural": "Composições de Equipe",
            },
        ),
        migrations.CreateModel(
            name="FuncaoEquipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "salario",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=10,
                        verbose_name="Salário",
                    ),
                ),
                (
                    "quantidade_funcionarios",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                (
                    "periculosidade",
                    models.BooleanField(default=False, verbose_name="Periculosidade"),
                ),
                (
                    "horas_extras_50",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Horas Extras 50%"
                    ),
                ),
                (
                    "horas_extras_100",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Horas Extras 100%"
                    ),
                ),
                (
                    "horas_sobreaviso",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Horas de Sobreaviso (1/3)"
                    ),
                ),
                (
                    "horas_prontidao",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Horas de Prontidão (2/3)"
                    ),
                ),
                (
                    "horas_adicional_noturno",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Horas Adicional Noturno"
                    ),
                ),
                (
                    "outros_custos",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        max_digits=10,
                        verbose_name="Outros Custos",
                    ),
                ),
                (
                    "composicao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="funcoes",
                        to="cadastro_equipe.composicaoequipe",
                    ),
                ),
                (
                    "contrato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cad_contrato.cadastrocontrato",
                    ),
                ),
                (
                    "funcao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cadastro_equipe.funcao",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="composicaoequipe",
            constraint=models.UniqueConstraint(
                fields=("contrato", "regional", "escopo", "equipe"),
                name="unique_composicao_por_regional_escopo_equipe",
            ),
        ),
        migrations.AddConstraint(
            model_name="funcaoequipe",
            constraint=models.UniqueConstraint(
                fields=("contrato", "composicao", "funcao"),
                name="unique_funcao_por_composicao",
            ),
        ),
    ]
