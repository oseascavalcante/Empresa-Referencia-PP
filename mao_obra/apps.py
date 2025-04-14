from django.apps import AppConfig


class MaoObraConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mao_obra"

    def ready(self):
        import mao_obra.signals  # Importa os sinais