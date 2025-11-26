from django import forms
from django.forms import inlineformset_factory
from .models import Producto, ProductoItem
from articulos.models import Articulo


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'precio', 'stock', 'moneda', 'proveedor', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductoItemForm(forms.ModelForm):
    class Meta:
        model = ProductoItem
        fields = ['articulo', 'cantidad', 'precio_especial']
        widgets = {
            'articulo': forms.Select(attrs={'class': 'form-select articulo-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'precio_especial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Dejar vacío para usar precio normal'}),
        }

    def __init__(self, *args, **kwargs):
        org = kwargs.pop('organizacion', None)
        super().__init__(*args, **kwargs)
        if org:
            self.fields['articulo'].queryset = Articulo.objects.filter(organizacion=org, activo=True)
        else:
            self.fields['articulo'].queryset = Articulo.objects.filter(activo=True)


# Formset para manejar múltiples artículos por producto
ProductoItemFormSet = inlineformset_factory(
    Producto,
    ProductoItem,
    form=ProductoItemForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=True
)


from .models import Moneda, ConfiguracionTienda, CodigoProducto


class MonedaForm(forms.ModelForm):
    class Meta:
        model = Moneda
        fields = ['codigo', 'nombre', 'simbolo', 'cambio_a_usd', 'principal']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'simbolo': forms.TextInput(attrs={'class': 'form-control'}),
            'cambio_a_usd': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConfiguracionTiendaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionTienda
        fields = ['permitir_multimoneda', 'moneda_principal']
        widgets = {
            'permitir_multimoneda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'moneda_principal': forms.Select(attrs={'class': 'form-select'}),
        }


class CodigoProductoForm(forms.ModelForm):
    class Meta:
        model = CodigoProducto
        fields = ['codigo_barra', 'codigo_qr']
        widgets = {
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para generar automáticamente'}),
            'codigo_qr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para generar automáticamente'}),
        }


CodigoProductoFormSet = inlineformset_factory(
    Producto,
    CodigoProducto,
    form=CodigoProductoForm,
    fields=['codigo_barra', 'codigo_qr'],
    extra=1,
    can_delete=True
)
