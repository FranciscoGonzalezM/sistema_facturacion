from django.db import models
from django.core.exceptions import ValidationError
import uuid
from organizaciones.models import Organizacion


class Moneda(models.Model):
    codigo = models.CharField(max_length=3, unique=True)  # USD, NIO, EUR, etc.
    nombre = models.CharField(max_length=50)
    simbolo = models.CharField(max_length=5)
    cambio_a_usd = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    principal = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    class Meta:
        app_label = 'articulos'


class ConfiguracionTienda(models.Model):
    moneda_principal = models.ForeignKey(Moneda, on_delete=models.PROTECT)
    permitir_multimoneda = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Configuración: {self.moneda_principal}"
    
    class Meta:
        app_label = 'articulos'
        verbose_name = "Configuración de Tienda"
        verbose_name_plural = "Configuraciones de Tienda"


class ArticuloManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(activo=True)


class Articulo(models.Model):
    """
    Un artículo es un item individual que puede ser parte de un producto/combo.
    Ejemplo: Hamburguesa, Papas, Refresco son artículos individuales.
    """
    organizacion = models.ForeignKey(
        Organizacion, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='articulos'
    )
    categoria = models.ForeignKey(
        'categorias.Categoria',
        on_delete=models.CASCADE,
        verbose_name="Categoría"
    )
    proveedor = models.ForeignKey(
        'proveedores.Proveedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articulos',
        verbose_name="Proveedor"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Costo")
    moneda = models.ForeignKey(Moneda, on_delete=models.PROTECT, verbose_name="Moneda")
    stock = models.IntegerField(verbose_name="Stock disponible")
    stock_minimo = models.IntegerField(default=5, verbose_name="Stock mínimo")
    activo = models.BooleanField(
        default=True, 
        verbose_name="¿Activo?", 
        help_text="Desmarque para desactivar el artículo sin eliminarlo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    objects = ArticuloManager()  # Solo artículos activos
    all_objects = models.Manager()  # Todos los artículos

    class Meta:
        app_label = 'articulos'
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (Stock: {self.stock})"

    def clean(self):
        if self.stock < 0:
            raise ValidationError("El stock no puede ser negativo")

    @property
    def disponible(self):
        return self.activo and self.stock > 0
    
    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo


class CodigoArticulo(models.Model):
    """Códigos QR y de barras para artículos"""
    articulo = models.ForeignKey(
        Articulo, 
        on_delete=models.CASCADE, 
        related_name='codigos', 
        null=True, 
        blank=True
    )
    codigo_qr = models.CharField(max_length=100, blank=True, null=True, unique=True)
    codigo_barra = models.CharField(max_length=50, blank=True, null=True, unique=True)

    class Meta:
        app_label = 'articulos'
        verbose_name = "Código de Artículo"
        verbose_name_plural = "Códigos de Artículo"

    def save(self, *args, **kwargs):
        if not self.codigo_qr:
            self.codigo_qr = str(uuid.uuid4())
        if not self.codigo_barra:
            self.codigo_barra = str(uuid.uuid4())[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.articulo.nombre if self.articulo else 'Sin artículo'} - QR: {self.codigo_qr or 'N/A'} / Barra: {self.codigo_barra or 'N/A'}"


