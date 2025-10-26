from django.db import models
from categorias.models import Categoria
from django.core.exceptions import ValidationError
import uuid
# Añade esta importación para la relación con Proveedor
from proveedores.models import Proveedor

class Moneda(models.Model):
    codigo = models.CharField(max_length=3, unique=True)  # USD, NIO, EUR, etc.
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=5)
    cambio_a_usd = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    principal = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class ConfiguracionTienda(models.Model):
    moneda_principal = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    permitir_multimoneda = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Configuración: {self.moneda_principal}"
    
    class Meta:
        verbose_name = "Configuración de Tienda"
        verbose_name_plural = "Configuraciones de Tienda"
#///////
class ProductoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)

class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        verbose_name="Categoría"
    )
    # ✅ SOLO UNA definición de proveedor
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name="Proveedor"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, verbose_name="Moneda")
    stock = models.IntegerField(verbose_name="Stock disponible")
    activo = models.BooleanField(default=True, verbose_name="¿Activo?", help_text="Desmarque para desactivar el producto sin eliminarlo")

    objects = ProductoManager()  # Solo productos activos
    all_objects = models.Manager()  # Todos los productos

    class Meta:
        app_label = 'productos'
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"

    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo")

    @property
    def disponible(self):
        return self.activo and self.stock > 0

class CodigoProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='codigos', null=True, blank=True)
    codigo_qr = models.CharField(max_length=100, blank=True, null=True, unique=True)
    codigo_barra = models.CharField(max_length=50, blank=True, null=True, unique=True)

    class Meta:
        verbose_name = "Código de Producto"
        verbose_name_plural = "Códigos de Producto"

    def save(self, *args, **kwargs):
        if not self.codigo_qr:
            self.codigo_qr = str(uuid.uuid4())
        if not self.codigo_barra:
            self.codigo_barra = str(uuid.uuid4())[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre if self.producto else 'Sin producto'} - QR: {self.codigo_qr or 'N/A'} / Barra: {self.codigo_barra or 'N/A'}"