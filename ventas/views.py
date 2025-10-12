from django.shortcuts import render, redirect
from facturas.models import Factura
from django.contrib.auth.decorators import login_required

@login_required
def punto_venta(request):
    # Vista específica para el punto de venta
    if request.method == 'POST':
        # Lógica para crear factura rápida
        pass
    return render(request, 'ventas/punto_venta.html')

@login_required
def ventas_dia(request):
    # Reporte de ventas del día
    from django.utils import timezone
    hoy = timezone.now().date()
    ventas = Factura.objects.filter(fecha=hoy)
    total = sum(v.total for v in ventas)
    return render(request, 'ventas/reporte_dia.html', {
        'ventas': ventas,
        'total': total,
        'fecha': hoy
    })
