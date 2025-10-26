from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

class Factura(models.Model):
    TIPO_VENTA_CHOICES = [
        ('contado', 'Contado'),
        ('credito', 'Crédito'),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)
    usuario = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    tipo_venta = models.CharField(max_length=10, choices=TIPO_VENTA_CHOICES, default='contado')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pagada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vuelto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-fecha']

    def calcular_totales(self):
        """Calcula y actualiza todos los totales basados en los detalles"""
        detalles = self.detalles.all()
        
        # Calcular subtotal e IVA correctamente
        subtotal = sum(detalle.subtotal for detalle in detalles)
        
        # Calcular IVA solo para productos que lo tienen
        iva_total = sum(
            detalle.subtotal * Decimal('0.15') 
            for detalle in detalles 
            if detalle.iva
        )
        
        # Aplicar descuento (no puede hacer el subtotal negativo)
        subtotal_con_descuento = max(Decimal('0.00'), subtotal - self.descuento)
        
        # Calcular total final
        total_final = subtotal_con_descuento + iva_total
        
        # Actualizar los campos
        self.subtotal = subtotal
        self.iva_total = iva_total
        self.total = total_final
        
        # Evitar recursión usando update()
        Factura.objects.filter(id=self.id).update(
            subtotal=self.subtotal,
            iva_total=self.iva_total,
            total=self.total,
            actualizada_en=timezone.now()
        )

    def clean(self):
        """Validaciones adicionales"""
        if self.descuento < 0:
            raise ValidationError({'descuento': 'El descuento no puede ser negativo'})
        
        if self.descuento > self.subtotal:
            raise ValidationError({'descuento': 'El descuento no puede ser mayor al subtotal'})

    def save(self, *args, **kwargs):
        """Sobrescribir save para asegurar cálculos"""
        self.clean()
        super().save(*args, **kwargs)
        # No calcular totales aquí para evitar loops

    def __str__(self):
        return f"Factura #{self.id} - ${self.total:.2f}"

class DetalleFactura(models.Model):
    factura = models.ForeignKey(Factura, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    # Permitir null/blank temporalmente para evitar prompt en migraciones existentes.
    moneda = models.ForeignKey('productos.Moneda', on_delete=models.PROTECT, null=True, blank=True)
    iva = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Factura"

    def calcular_subtotal(self):
        """Calcula el subtotal del detalle"""
        return Decimal(self.cantidad) * self.precio_unitario

    def save(self, *args, **kwargs):
        """Asigna moneda por defecto desde el producto (si falta), calcula subtotal y guarda.

        Además actualiza los totales de la factura después de guardar.
        """
        # Si no se especifica moneda, intentar usar la del producto relacionado
        if not self.moneda_id and self.producto_id:
            try:
                self.moneda = self.producto.moneda
            except Exception:
                # si por alguna razón producto no tiene moneda, dejar como None
                self.moneda = None

        # Calcular subtotal a partir de cantidad y precio_unitario
        try:
            self.subtotal = Decimal(self.cantidad) * Decimal(self.precio_unitario)
        except Exception:
            # En caso de valores no válidos, asegurar que subtotal sea 0
            self.subtotal = Decimal('0.00')

        super().save(*args, **kwargs)

        # Actualizar totales de la factura después de guardar
        try:
            self.factura.calcular_totales()
        except Exception:
            pass

    def clean(self):
        """Validaciones del detalle"""
        if self.cantidad < 1:
            raise ValidationError({'cantidad': 'La cantidad debe ser al menos 1'})
        
        if self.precio_unitario <= 0:
            raise ValidationError({'precio_unitario': 'El precio debe ser mayor a 0'})
        
        # Verificar stock solo si el producto existe y tiene stock
        if self.producto_id and hasattr(self.producto, 'stock'):
            if self.producto.stock < self.cantidad:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente. Disponible: {self.producto.stock}'
                })

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} - ${self.subtotal:.2f}"
    
    # Campos para pagos con tarjeta
    metodo_pago = models.CharField(max_length=20, default='efectivo', choices=[
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia')
    ])
    id_transaccion = models.CharField(max_length=100, blank=True, null=True)
    ultimos_digitos = models.CharField(max_length=4, blank=True, null=True)
    tipo_tarjeta = models.CharField(max_length=20, blank=True, null=True)
    estado_pago = models.CharField(max_length=20, default='pendiente', choices=[
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido')
    ])
    
    # Nota: la propiedad subtotal se manejaba por campo y por property; se eliminó la property