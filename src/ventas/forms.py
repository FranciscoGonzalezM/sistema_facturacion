from django import forms
from facturas.models import Factura, DetalleFactura
from inventario.models import Producto

class VentaRapidaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all())
    productos = forms.ModelMultipleChoiceField(
        queryset=Producto.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple
    )
    
    def save(self):
        # Lógica para crear factura y detalles automáticamente
        pass