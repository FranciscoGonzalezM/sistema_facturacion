from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

# Relaciones a otras apps
from organizaciones.models import Organizacion
from categorias.models import Categoria
from proveedores.models import Proveedor
from articulos.models import Articulo


class ProductoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)


class Moneda(models.Model):
    codigo = models.CharField(max_length=3, unique=True)
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=5)
    cambio_a_usd = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('1.0'))
    principal = models.BooleanField(default=False)

    class Meta:
        app_label = 'productos'

    def __str__(self):
        return f"{self.nombre} ({self.simbolo})"


class ConfiguracionTienda(models.Model):
    permitir_multimoneda = models.BooleanField(default=False)
    moneda_principal = models.ForeignKey(Moneda, on_delete=models.PROTECT)

    class Meta:
        app_label = 'productos'
        verbose_name = 'Configuración de Tienda'
        verbose_name_plural = 'Configuraciones de Tienda'

    def __str__(self):
        return f"Configuración (Moneda: {self.moneda_principal})"


class CodigoProducto(models.Model):
    codigo_qr = models.CharField(max_length=100, unique=True, null=True, blank=True)
    codigo_barra = models.CharField(max_length=50, unique=True, null=True, blank=True)
    producto = models.ForeignKey('Producto', related_name='codigos', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        app_label = 'productos'
        verbose_name = 'Código de Producto'
        verbose_name_plural = 'Códigos de Producto'

    def __str__(self):
        return self.codigo_barra or self.codigo_qr or f"Código #{self.pk}"


class Producto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio', default=Decimal('0.00'))
    stock = models.IntegerField(verbose_name='Stock disponible', default=0)
    activo = models.BooleanField(default=True, help_text='Desmarque para desactivar el producto sin eliminarlo', verbose_name='¿Activo?')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name='Categoría')
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, verbose_name='Moneda', null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos', verbose_name='Proveedor')
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, null=True, blank=True, related_name='productos')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    objects = ProductoManager()
    all_objects = models.Manager()

    class Meta:
        app_label = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        symbol = self.moneda.simbolo if self.moneda else '$'
        return f"{self.nombre} - {symbol}{self.precio}"

    @property
    def disponible(self):
        return self.activo and self.stock > 0


class ProductoItem(models.Model):
    """
    Relación entre Producto y Artículo.
    Permite definir qué artículos componen un producto/combo y en qué cantidad.
    """
    producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name="Producto"
    )
    articulo = models.ForeignKey(
        'articulos.Articulo',
        on_delete=models.CASCADE,
        related_name='en_productos',
        verbose_name="Artículo"
    )
    cantidad = models.PositiveIntegerField(
        default=1, 
        verbose_name="Cantidad"
    )
    precio_especial = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Precio Especial",
        help_text="Dejar vacío para usar el precio del artículo"
    )

    class Meta:
        app_label = 'productos'
        verbose_name = "Artículo del Producto"
        verbose_name_plural = "Artículos del Producto"
        unique_together = ['producto', 'articulo']

    def __str__(self):
        return f"{self.cantidad}x {self.articulo.nombre} en {self.producto.nombre}"

    @property
    def precio_unitario(self):
        """Precio unitario del artículo (especial o normal)"""
        if self.precio_especial is not None:
            return self.precio_especial
        return self.articulo.precio

    @property
    def subtotal(self):
        """Subtotal de este item (precio * cantidad)"""
        return self.precio_unitario * self.cantidad

    def clean(self):
        if self.cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0")
