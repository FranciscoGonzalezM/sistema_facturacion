from django.core.management.base import BaseCommand
from productos.models import Moneda, ConfiguracionTienda

class Command(BaseCommand):
    help = 'Inicializa las monedas básicas y la configuración de la tienda'
    
    def handle(self, *args, **options):
        # Crear monedas básicas
        usd, created = Moneda.objects.get_or_create(
            codigo='USD',
            defaults={
                'nombre': 'Dólar Estadounidense',
                'simbolo': '$',
                'cambio_a_usd': 1.0,
                'principal': False
            }
        )
        
        nio, created = Moneda.objects.get_or_create(
            codigo='NIO',
            defaults={
                'nombre': 'Córdoba Nicaragüense',
                'simbolo': 'C$',
                'cambio_a_usd': 0.027,  # Valor aproximado
                'principal': True  # Establecer como principal para Nicaragua
            }
        )
        
        eur, created = Moneda.objects.get_or_create(
            codigo='EUR',
            defaults={
                'nombre': 'Euro',
                'simbolo': '€',
                'cambio_a_usd': 1.18,
                'principal': False
            }
        )
        
        # Configurar la tienda
        config, created = ConfiguracionTienda.objects.get_or_create(
            id=1,
            defaults={
                'moneda_principal': nio,
                'permitir_multimoneda': True
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS('Monedas y configuración inicializadas correctamente')
        )