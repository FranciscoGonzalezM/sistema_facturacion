from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied
import requests
from decimal import Decimal
from django.conf import settings
from .models import Moneda

# ==================== FUNCIONES DE PERMISOS ====================
def es_admin(user):
    """Verifica si el usuario es administrador o superusuario"""
    return user.groups.filter(name='Administrador').exists() or user.is_superuser

def es_cajero(user):
    """Verifica si el usuario es cajero"""
    return user.groups.filter(name='Cajero').exists()

def es_cajero_o_admin(user):
    """Verifica si el usuario tiene rol de cajero o administrador"""
    return es_cajero(user) or es_admin(user)

# ==================== DECORADORES PERSONALIZADOS ====================
def admin_required(view_func):
    """Decorador para vistas que requieren rol de administrador"""
    def wrapper(request, *args, **kwargs):
        if not es_admin(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def cajero_required(view_func):
    """Decorador para vistas que requieren rol de cajero"""
    def wrapper(request, *args, **kwargs):
        if not es_cajero_o_admin(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

# ==================== FUNCIONES DE HELPERS ====================
def obtener_estadisticas():
    """
    Retorna estadísticas básicas del sistema
    Uso en vistas del dashboard
    """
    from clientes.models import Cliente
    from productos.models import Producto
    from facturas.models import Factura
    
    return {
        'total_clientes': Cliente.objects.count(),
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_facturas': Factura.objects.count(),
        'facturas_hoy': Factura.objects.filter(fecha__date=timezone.now().date()).count()
    }

def crear_log_accion(usuario, accion):
    """Registra una acción en el log del sistema"""
    from core.models import Actividad
    Actividad.objects.create(usuario=usuario, accion=accion)

# ==================== VALIDACIONES ====================
def validar_stock(producto, cantidad):
    """Valida si hay suficiente stock disponible"""
    if not producto.activo:
        raise ValueError("El producto no está activo")
    if producto.stock < cantidad:
        raise ValueError(f"Stock insuficiente. Disponible: {producto.stock}")
    return True

def obtener_tasa_cambio(origen, destino):
    """
    Obtiene la tasa de cambio entre dos monedas
    Puedes implementar esta función con una API como exchangerate-api.com
    """
    # Ejemplo simplificado - en producción usar una API real
    if origen == destino:
        return Decimal('1.0')
    
    # Tasas de cambio de ejemplo (deberías obtenerlas de una API)
    tasas = {
        'USD': {'NIO': Decimal('36.50'), 'EUR': Decimal('0.85')},
        'NIO': {'USD': Decimal('0.027'), 'EUR': Decimal('0.023')},
        'EUR': {'USD': Decimal('1.18'), 'NIO': Decimal('43.10')},
    }
    
    if origen in tasas and destino in tasas[origen]:
        return tasas[origen][destino]
    
    return Decimal('1.0')

def convertir_moneda(monto, moneda_origen, moneda_destino):
    """Convierte un monto de una moneda a otra"""
    if moneda_origen == moneda_destino:
        return monto
    
    tasa = obtener_tasa_cambio(moneda_origen.codigo, moneda_destino.codigo)
    return monto * tasa