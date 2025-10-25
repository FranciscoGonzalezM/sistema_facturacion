# facturas/signals.py (versión corregida)
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DetalleFactura

@receiver(post_save, sender=DetalleFactura)
def actualizar_stock(sender, instance, created, **kwargs):
    """Actualiza el stock cuando se crea un detalle de factura"""
    if created:
        producto = instance.producto
        producto.stock -= instance.cantidad
        producto.save(update_fields=['stock'])