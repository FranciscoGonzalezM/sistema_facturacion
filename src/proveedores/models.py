from django.db import models
from django.core.validators import RegexValidator

class Proveedor(models.Model):
    TIPO_PROVEEDOR = [
        ('productos', 'Productos'),
        ('servicios', 'Servicios'),
        ('ambos', 'Productos y Servicios'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('pendiente', 'Pendiente'),
    ]

    nombre_empresa = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    nombre_contacto = models.CharField(max_length=100, verbose_name="Nombre de Contacto")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número de teléfono debe tener entre 9 y 15 dígitos."
    )
    telefono = models.CharField(validators=[telefono_regex], max_length=15, verbose_name="Teléfono")
    direccion = models.TextField(verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")
    pais = models.CharField(max_length=100, verbose_name="País", default="México")
    rfc = models.CharField(max_length=13, verbose_name="RFC", blank=True, null=True)
    tipo_proveedor = models.CharField(max_length=20, choices=TIPO_PROVEEDOR, verbose_name="Tipo de Proveedor")
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo', verbose_name="Estado")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    # Relación con categorías de productos
    categorias = models.ManyToManyField(
        'categorias.Categoria',
        related_name='proveedores',
        blank=True,
        verbose_name="Categorías de Productos"
    )

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre_empresa']

    def __str__(self):
        return self.nombre_empresa

    def productos_relacionados(self):
        """Obtiene los productos relacionados a través de las categorías"""
        from productos.models import Producto
        return Producto.objects.filter(categoria__in=self.categorias.all())

    # NUEVO: Método para obtener productos directamente asociados al proveedor
    def productos_directos(self):
        """Obtiene los productos directamente asociados a este proveedor"""
        return self.productos.all()


class ContactoProveedor(models.Model):
    TIPO_CONTACTO = [
        ('principal', 'Contacto Principal'),
        ('ventas', 'Ventas'),
        ('soporte', 'Soporte Técnico'),
        ('administracion', 'Administración'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    puesto = models.CharField(max_length=100, verbose_name="Puesto")
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono", blank=True, null=True)
    tipo_contacto = models.CharField(max_length=15, choices=TIPO_CONTACTO, verbose_name="Tipo de Contacto")
    es_principal = models.BooleanField(default=False, verbose_name="Contacto Principal")

    class Meta:
        verbose_name = "Contacto de Proveedor"
        verbose_name_plural = "Contactos de Proveedores"

    def __str__(self):
        return f"{self.nombre} - {self.proveedor.nombre_empresa}"


class PedidoProveedor(models.Model):
    ESTADO_PEDIDO = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('en_camino', 'En Camino'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado'),
    ]

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='pedidos')
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Pedido")
    fecha_esperada = models.DateField(verbose_name="Fecha Esperada de Entrega")
    fecha_recibido = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Recepción")
    estado = models.CharField(max_length=15, choices=ESTADO_PEDIDO, default='pendiente', verbose_name="Estado")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total del Pedido")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas del Pedido")

    class Meta:
        verbose_name = "Pedido a Proveedor"
        verbose_name_plural = "Pedidos a Proveedores"
        ordering = ['-fecha_pedido']

    def __str__(self):
        return f"Pedido #{self.id} - {self.proveedor.nombre_empresa}"

    def calcular_total(self):
        """Calcula el total del pedido sumando los items"""
        return sum(item.subtotal() for item in self.items.all())


class ItemPedido(models.Model):
    pedido = models.ForeignKey(PedidoProveedor, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=16, verbose_name="IVA (%)")

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def total_con_iva(self):
        subtotal = self.subtotal()
        iva_monto = subtotal * (self.iva / 100)
        return subtotal + iva_monto