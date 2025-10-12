from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Actividad(models.Model):
    TIPO_CHOICES = [
        ('cliente', 'Cliente'),
        ('producto', 'Producto'),
        ('venta', 'Venta'),
        ('sistema', 'Sistema'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actividades_dashboard')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = 'Actividades'
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha.strftime('%d/%m/%Y %H:%M')}"
