from django.db import models
from organizaciones.models import Organizacion

class Cliente(models.Model):
    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, null=True, blank=True, related_name='clientes')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    nit = models.CharField(max_length=20, blank=True, null=True)
    ciudad = models.CharField(max_length=50, blank=True, null=True)
      # ✅ Campo activo
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Activo?",
        help_text="Desmarque para desactivar el cliente sin eliminarlo"
    )
  
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    def __str__(self):
        return f"{self.nombre} {self.apellido}"