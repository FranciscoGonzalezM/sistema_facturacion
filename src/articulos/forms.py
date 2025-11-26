from django import forms
from django.forms import inlineformset_factory
from .models import Articulo, CodigoArticulo, Moneda, ConfiguracionTienda


class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['categoria', 'proveedor', 'nombre', 'descripcion', 'precio', 'costo', 'moneda', 'stock', 'stock_minimo', 'activo']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CodigoArticuloForm(forms.ModelForm):
    class Meta:
        model = CodigoArticulo
        fields = ['codigo_qr', 'codigo_barra']
        widgets = {
            'codigo_qr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Se genera automáticamente si se deja vacío'}),
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Se genera automáticamente si se deja vacío'}),
        }


# Formset para manejar múltiples códigos por artículo
CodigoArticuloFormSet = inlineformset_factory(
    Articulo,
    CodigoArticulo,
    form=CodigoArticuloForm,
    extra=1,
    can_delete=True
)


class MonedaForm(forms.ModelForm):
    class Meta:
        model = Moneda
        fields = ['codigo', 'nombre', 'simbolo', 'cambio_a_usd', 'principal']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'simbolo': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 5}),
            'cambio_a_usd': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ConfiguracionTiendaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionTienda
        fields = ['moneda_principal', 'permitir_multimoneda']
        widgets = {
            'moneda_principal': forms.Select(attrs={'class': 'form-select'}),
            'permitir_multimoneda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


