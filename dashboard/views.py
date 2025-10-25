
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum, Q
from clientes.models import Cliente
from productos.models import Producto, Categoria
from ventas.models import Factura
from .models import Actividad
from django.http import JsonResponse


def panel_administracion(request):
    # Totales generales
    total_clientes = Cliente.objects.count()
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_facturas = Factura.objects.count()
    
    # Estadísticas mensuales
    mes_actual = timezone.now().month
    nuevos_clientes = Cliente.objects.filter(
        fecha_registro__month=mes_actual
    ).count()
    
    productos_bajo_stock = Producto.objects.filter(
        stock__lt=10
    ).count()
    
    ventas_mes_actual = Factura.objects.filter(
        fecha__month=mes_actual
    ).count()
    
    ingresos_mes_actual = Factura.objects.filter(
        fecha__month=mes_actual
    ).aggregate(Sum('total'))['total__sum'] or 0
    
    facturas_pendientes = Factura.objects.filter(
        estado='pendiente'
    ).count()
    
    # Actividad reciente
    actividad_reciente = Actividad.objects.all().order_by('-fecha')[:5]
    
    context = {
        'total_clientes': total_clientes,
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_facturas': total_facturas,
        'nuevos_clientes': nuevos_clientes,
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_mes_actual': ventas_mes_actual,
        'ingresos_mes_actual': ingresos_mes_actual,
        'facturas_pendientes': facturas_pendientes,
        'actividad_reciente': actividad_reciente,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


def dashboard_data(request):
    # Datos de ejemplo, luego los traerás de la base de datos
    data = {
        'nuevos_clientes': 10,
        'ventas_mes': 5000,
        'productos_bajos_stock': 3
    }
    return JsonResponse(data)