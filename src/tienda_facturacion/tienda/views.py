from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from productos.models import Producto
from clientes.models import Cliente
from facturas.models import Factura


@login_required
def panel_administracion(request):
    context = {
        'total_productos': Producto.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_facturas': Factura.objects.count(),
    }
    return render(request, 'tienda/dashboard.html', context)

