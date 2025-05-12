# custo_direto/apps.py

from django.apps import AppConfig

class CustoDiretoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custo_direto'

    def ready(self):
        import custo_direto.signals  # noqa
