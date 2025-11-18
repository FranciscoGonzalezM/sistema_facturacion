from django.contrib import admin
from .models import Organizacion, Miembro


class MiembroInline(admin.TabularInline):
    model = Miembro
    extra = 0


@admin.register(Organizacion)
class OrganizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'dominio', 'fecha_creacion')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [MiembroInline]


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ('user', 'organizacion', 'role', 'es_propietario', 'fecha_agregado')
    list_filter = ('role', 'es_propietario')
