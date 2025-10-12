from facturas.models import Factura, DetalleFactura
from datetime import date

def crear_venta_rapida(cliente, productos):
    """Crea una factura de venta rápida"""
    factura = Factura.objects.create(cliente=cliente, total=0)
    
    for producto in productos:
        DetalleFactura.objects.create(
            factura=factura,
            producto=producto,
            cantidad=1,
            precio_unitario=producto.precio_venta,
            subtotal=producto.precio_venta
        )
    
    return factura

def ventas_por_periodo(inicio, fin):
    """Reporte de ventas por periodo"""
    return Factura.objects.filter(fecha__range=(inicio, fin))