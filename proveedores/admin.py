from django.contrib import admin

from django.contrib import admin
from .models import Proveedor, ContactoProveedor, PedidoProveedor, ItemPedido

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1

class ContactoProveedorInline(admin.TabularInline):
    model = ContactoProveedor
    extra = 1

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'nombre_contacto', 'email', 'telefono', 'ciudad', 'tipo_proveedor', 'estado')
    list_filter = ('tipo_proveedor', 'estado', 'ciudad', 'categorias')
    search_fields = ('nombre_empresa', 'nombre_contacto', 'email', 'rfc')
    filter_horizontal = ('categorias',)
    inlines = [ContactoProveedorInline]
    list_per_page = 20

@admin.register(ContactoProveedor)
class ContactoProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puesto', 'email', 'proveedor', 'tipo_contacto', 'es_principal')
    list_filter = ('tipo_contacto', 'es_principal')
    search_fields = ('nombre', 'proveedor__nombre_empresa', 'email')
    list_per_page = 20

@admin.register(PedidoProveedor)
class PedidoProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'fecha_pedido', 'fecha_esperada', 'estado', 'total')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('proveedor__nombre_empresa', 'id')
    inlines = [ItemPedidoInline]
    list_per_page = 20

@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('pedido__proveedor',)
    search_fields = ('producto__nombre', 'pedido__id')
