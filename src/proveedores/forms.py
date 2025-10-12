from django import forms
from .models import Proveedor, ContactoProveedor, PedidoProveedor, ItemPedido
# Añade esta importación para la relación con Producto
from productos.models import Producto

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre_empresa', 'nombre_contacto', 'email', 'telefono', 
            'direccion', 'ciudad', 'pais', 'rfc', 'tipo_proveedor', 
            'estado', 'categorias', 'notas'
        ]
        widgets = {
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'rfc': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_proveedor': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ContactoProveedorForm(forms.ModelForm):
    class Meta:
        model = ContactoProveedor
        fields = ['nombre', 'puesto', 'email', 'telefono', 'tipo_contacto', 'es_principal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_contacto': forms.Select(attrs={'class': 'form-control'}),
        }

class PedidoProveedorForm(forms.ModelForm):
    class Meta:
        model = PedidoProveedor
        fields = ['fecha_esperada', 'notas']  # Especifica explícitamente los campos que quieres incluir
        widgets = {
            'fecha_esperada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['producto', 'cantidad', 'precio_unitario', 'iva']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
            'iva': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # Filtrar productos por proveedor del pedido (se puede implementar en la vista)
    def __init__(self, *args, **kwargs):
        proveedor_id = kwargs.pop('proveedor_id', None)
        super().__init__(*args, **kwargs)
        
        if proveedor_id:
            # Filtrar productos que pertenecen a este proveedor
            self.fields['producto'].queryset = Producto.objects.filter(proveedor_id=proveedor_id)