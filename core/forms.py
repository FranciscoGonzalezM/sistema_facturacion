from django import forms
from django.forms import inlineformset_factory
from django.db import models
from clientes.models import Cliente
from productos.models import Producto, CodigoProducto
from facturas.models import Factura, DetalleFactura


# ---------------------------
# Formulario de Factura
# ---------------------------
class FacturaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(), 
        label="Cliente",
        widget=forms.Select(attrs={'class': 'form-control select2', 'required': 'required'})
    )

    class Meta:
        model = Factura
        fields = ['cliente']


# ---------------------------
# Formulario de Detalle de Factura
# ---------------------------
class DetalleFacturaForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control select2 producto-select', 'required': 'required'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control cantidad', 'min': '1', 'required': 'required'})
    )

    class Meta:
        model = DetalleFactura
        fields = ['producto', 'cantidad']
        exclude = ['precio_unitario', 'subtotal']

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        producto = self.cleaned_data.get('producto')
        if producto and cantidad > producto.stock:
            raise forms.ValidationError(f"Stock insuficiente. Máximo disponible: {producto.stock}")
        return cantidad


# Formset para detalles de factura
DetalleFacturaFormSet = inlineformset_factory(
    Factura,
    DetalleFactura,
    form=DetalleFacturaForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


# ---------------------------
# Formulario de Producto
# ---------------------------
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'precio', 'stock', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ---------------------------
# Formulario para códigos de Producto
# ---------------------------
class CodigoProductoForm(forms.ModelForm):
    class Meta:
        model = CodigoProducto
        fields = ['codigo_barra', 'codigo_qr']
        widgets = {
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para generar automáticamente'}),
            'codigo_qr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para generar automáticamente'}),
        }


# Formset para códigos de Producto
CodigoProductoFormSet = inlineformset_factory(
    Producto,
    CodigoProducto,
    form=CodigoProductoForm,
    fields=['codigo_barra', 'codigo_qr'],
    extra=1,
    can_delete=True
)


# ---------------------------
# Formulario de búsqueda de productos
# ---------------------------
class BuscarProductoForm(forms.Form):
    busqueda = forms.CharField(
        label="Código QR, Código de Barras o Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escanee código o escriba nombre...', 'autofocus': 'autofocus'})
    )

    def buscar_producto(self):
        valor = self.cleaned_data.get('busqueda', '').strip()
        if valor:
            return Producto.objects.filter(
                activo=True
            ).filter(
                models.Q(codigos__codigo_qr=valor) |
                models.Q(codigos__codigo_barra=valor) |
                models.Q(nombre__icontains=valor)
            ).distinct()
        return Producto.objects.none()