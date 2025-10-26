# facturas/apps.py
from django.apps import AppConfig

class FacturasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.facturas'

    def ready(self):
        # Importa las señales cuando la app esté lista
        import facturas.signals
