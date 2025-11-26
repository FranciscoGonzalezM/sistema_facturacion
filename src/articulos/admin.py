from django.contrib import admin
from .models import Articulo, CodigoArticulo, Moneda, ConfiguracionTienda


class CodigoArticuloInline(admin.TabularInline):
    model = CodigoArticulo
    extra = 1


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'activo', 'organizacion']
    list_filter = ['categoria', 'activo', 'organizacion']
    search_fields = ['nombre', 'descripcion']
    inlines = [CodigoArticuloInline]


@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'simbolo', 'cambio_a_usd', 'principal']


@admin.register(ConfiguracionTienda)
class ConfiguracionTiendaAdmin(admin.ModelAdmin):
    list_display = ['moneda_principal', 'permitir_multimoneda']


