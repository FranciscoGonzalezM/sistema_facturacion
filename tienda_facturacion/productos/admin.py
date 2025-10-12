# productos/admin.py
from django.contrib import admin
from .models import Producto, CodigoProducto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'activo', 'disponible']
    list_filter = ['activo', 'categoria']
    list_editable = ['activo', 'stock']  # Para editar fácilmente
    
    # MOSTRAR TODOS LOS PRODUCTOS, NO SOLO LOS ACTIVOS
    def get_queryset(self, request):
        return Producto.all_objects.all()

@admin.register(CodigoProducto)
class CodigoProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'codigo_barra', 'codigo_qr', 'get_categoria']
    list_filter = ['producto__categoria']
    search_fields = ['producto__nombre', 'codigo_barra', 'codigo_qr']
    
    def get_categoria(self, obj):
        return obj.producto.categoria if obj.producto else 'N/A'
    get_categoria.short_description = 'Categoría'