
from django.db import models
from django.contrib.auth.models import User
from productos.models import Producto  # Ajusta si tu app de productos tiene otro nombre

class Requiza(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Requiza de {self.cantidad} {self.producto.nombre} - {self.motivo}"
