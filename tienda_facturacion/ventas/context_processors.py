from datetime import date
from facturas.models import Factura

def ventas_hoy(request):
    if request.user.is_authenticated:
        return {
            'ventas_hoy_count': Factura.objects.filter(fecha=date.today()).count(),
            'ventas_hoy_total': sum(f.total for f in Factura.objects.filter(fecha=date.today()))
        }
    return {}