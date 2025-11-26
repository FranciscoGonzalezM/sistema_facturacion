from django.contrib import admin
from .models import Producto, ProductoItem


class ProductoItemInline(admin.TabularInline):
    model = ProductoItem
    extra = 1
    # Avoid autocomplete reference to Articulo if admin for that model is not registered
    # autocomplete_fields = ['articulo']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'activo', 'organizacion', 'moneda']
    list_filter = ['activo', 'organizacion', 'moneda']
    search_fields = ['nombre']
    inlines = [ProductoItemInline]
    
