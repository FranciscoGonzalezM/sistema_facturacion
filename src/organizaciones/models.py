from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Organizacion(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    dominio = models.CharField(max_length=255, blank=True, null=True, help_text='Dominio opcional para tenant (ej: empresa.example.com)')
    logo = models.ImageField(upload_to='organizaciones/logos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Organización'
        verbose_name_plural = 'Organizaciones'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Miembro(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('user', 'User'),
        ('cajero', 'Cajero'),
    )

    organizacion = models.ForeignKey(Organizacion, on_delete=models.CASCADE, related_name='miembros')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizaciones')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    es_propietario = models.BooleanField(default=False)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Miembro'
        verbose_name_plural = 'Miembros'
        unique_together = (('organizacion', 'user'),)

    def __str__(self):
        return f"{self.user.get_username()} @ {self.organizacion.nombre} ({self.role})"
