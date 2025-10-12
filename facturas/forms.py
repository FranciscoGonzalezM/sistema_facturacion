from django import forms
from .models import Factura, DetalleFactura

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'tipo_venta', 'descuento']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-control'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields = ['producto', 'cantidad', 'precio_unitario', 'iva']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control producto-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control cantidad', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control precio', 'step': '0.01'}),
            'iva': forms.CheckboxInput(attrs={'class': 'form-check-input iva-checkbox'}),
        }

# Formset para múltiples detalles
DetalleFacturaFormSet = forms.formset_factory(
    DetalleFacturaForm,
    extra=1,
    can_delete=False
)