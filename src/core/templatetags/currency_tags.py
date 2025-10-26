# templatetags/currency_tags.py
from django import template
from django.conf import settings
from productos.models import ConfiguracionTienda

register = template.Library()

@register.filter
def format_currency(value, moneda=None):
    """Formatea un valor como moneda"""
    if value is None:
        return ""
    
    if not moneda:
        # Obtener la moneda principal por defecto desde la configuración de tienda
        try:
            config = ConfiguracionTienda.objects.first()
            if config and getattr(config, 'moneda_principal', None):
                moneda = config.moneda_principal
            else:
                # Fallback a una moneda común (NIO) si existe
                from productos.models import Moneda
                moneda = Moneda.objects.filter(codigo__iexact='NIO').first() or Moneda.objects.first()
        except Exception:
            # En caso de error usar formato con C$ por defecto
            return f"C$ {value:,.2f}"
    
    # Formatear según la moneda
    code = getattr(moneda, 'codigo', '')
    if not code:
        return f"{value:,.2f}"
    code = code.upper()
    simbolo = getattr(moneda, 'simbolo', None)
    if simbolo:
        return f"{simbolo} {value:,.2f}"
    # Fallbacks por código
    if code == 'USD':
        return f"$ {value:,.2f}"
    if code == 'NIO':
        return f"C$ {value:,.2f}"
    if code == 'EUR':
        return f"€ {value:,.2f}"
    return f"{value:,.2f} {code}"