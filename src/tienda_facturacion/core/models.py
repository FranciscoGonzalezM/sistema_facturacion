from django.db import models
from django.contrib.auth.models import User

class Actividad(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='actividades_core'
    )
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario.username} - {self.accion[:50]}..."