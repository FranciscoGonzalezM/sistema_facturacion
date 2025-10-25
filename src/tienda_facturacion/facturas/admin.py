from django.contrib import admin
from .models import Factura

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    # Columnas que se mostrarán en la lista del admin
    list_display = ('id', 'cliente', 'fecha', 'total')
    
    # Campos por los que se podrá buscar
    search_fields = ('id', 'cliente__nombre', 'cliente__apellido')
    
    # Filtros en el panel lateral
    list_filter = ('fecha',)
    
    # Orden por defecto (últimas facturas primero)
    ordering = ('-fecha',)
    
    # Cuántos registros mostrar por página
    list_per_page = 20

    # Mostrar un selector de fecha avanzado
    date_hierarchy = 'fecha'

    # Campos de solo lectura (si no quieres que se editen desde el admin)
    readonly_fields = ('fecha',)

    # Personalizar el formulario (opcional)
    fieldsets = (
        ("Información de la Factura", {
            'fields': ('cliente', 'fecha', 'estado', 'total')
        }),
        ("Detalles Adicionales", {
            'fields': ('descripcion',),  # si tienes este campo
            'classes': ('collapse',),    # lo hace colapsable
        }),
    )

