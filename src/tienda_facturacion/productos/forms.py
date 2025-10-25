from django import forms
from .models import Producto, CodigoProducto, Moneda, ConfiguracionTienda
from django.forms import inlineformset_factory
from proveedores.models import Proveedor

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'proveedor', 'nombre', 'precio', 'moneda', 'stock', 'activo']  # AÑADIDO 'moneda'
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'moneda': forms.Select(attrs={'class': 'form-control'}),  # NUEVO widget para moneda
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar proveedores activos
        self.fields['proveedor'].queryset = Proveedor.objects.filter(estado='activo')
        self.fields['proveedor'].required = False
        
        # Configurar el campo moneda
        self.fields['moneda'].queryset = Moneda.objects.all()
        
        # Establecer moneda principal por defecto
        try:
            config = ConfiguracionTienda.objects.first()
            if config and config.moneda_principal:
                self.fields['moneda'].initial = config.moneda_principal
        except Exception:
            # Si hay error, usar la primera moneda disponible o crear una por defecto
            moneda_default = Moneda.objects.filter(principal=True).first()
            if moneda_default:
                self.fields['moneda'].initial = moneda_default
            elif Moneda.objects.exists():
                self.fields['moneda'].initial = Moneda.objects.first()
        
        # Si no hay monedas, mostrar advertencia
        if not Moneda.objects.exists():
            self.fields['moneda'].help_text = "⚠️ No hay monedas configuradas. Contacte al administrador."

class CodigoProductoForm(forms.ModelForm):
    class Meta:
        model = CodigoProducto
        fields = ['codigo_qr', 'codigo_barra']
        widgets = {
            'codigo_qr': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código QR (auto-generado si está vacío)'}),
            'codigo_barra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de barras (auto-generado si está vacío)'}),
        }

# Formset para códigos de producto
CodigoProductoFormSet = inlineformset_factory(
    Producto, 
    CodigoProducto, 
    form=CodigoProductoForm,
    extra=1,
    can_delete=True,
    max_num=5,
)

class MonedaForm(forms.ModelForm):
    class Meta:
        model = Moneda
        fields = ['codigo', 'nombre', 'simbolo', 'cambio_a_usd', 'principal']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'simbolo': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '5'}),
            'cambio_a_usd': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_principal(self):
        principal = self.cleaned_data.get('principal')
        if principal:
            # Si se marca como principal, quitar principal de otras monedas
            Moneda.objects.filter(principal=True).update(principal=False)
        return principal

class ConfiguracionTiendaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionTienda
        fields = ['moneda_principal', 'permitir_multimoneda']
        widgets = {
            'moneda_principal': forms.Select(attrs={'class': 'form-control'}),
            'permitir_multimoneda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }