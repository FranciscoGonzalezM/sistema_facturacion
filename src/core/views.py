from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import JsonResponse
from clientes.models import Cliente
from productos.models import Producto, CodigoProducto
from productos.forms import CodigoProductoFormSet
from categorias.models import Categoria
from facturas.models import Factura
from .models import Actividad
from django.utils import timezone
from django.db.models import Sum
from requiza.models import Requiza
from .forms import ProductoForm
from organizaciones.forms import OrganizacionLoginForm


# --- Función para verificar si es admin ---
def es_admin(user):
    return user.is_staff

# --- Función para verificar si es cajero o admin ---
def es_cajero_o_admin(user):
    return user.is_staff or user.groups.filter(name='cajeros').exists()

# --- Vista para el panel de administrador ---
@login_required
@user_passes_test(es_admin)
def admin_inicio(request):
    total_requizas = Requiza.objects.count()
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_facturas': Factura.objects.count(),
        'total_requizas': total_requizas,
    }
    return render(request, 'registration/admin_inicio.html', context)
        
# --- Vista de inicio que redirige según rol ---
@login_required
def inicio(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        return redirect('admin_inicio')
    elif user.groups.filter(name='cajeros').exists():
        return redirect('facturar')
    else:
        messages.error(request, "No tienes permisos para acceder.")
        return redirect('login')

# --- Vista de login manual ---
def custom_logout(request):
    logout(request)
    return redirect('login')

# --- Vista de login usando clase de Django ---
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = OrganizacionLoginForm

    def form_valid(self, form):
        # Authenticate using company + username + password via our TenantBackend
        company = form.cleaned_data.get('company')
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, company=company, username=username, password=password)
        if user is None:
            form.add_error(None, 'Credenciales inválidas para la empresa/usuario proporcionado')
            return self.form_invalid(form)
        login(self.request, user)
        # Guardar la organización en sesión para uso posterior
        from organizaciones.models import Organizacion
        org = Organizacion.objects.filter(nombre__iexact=company).first() or Organizacion.objects.filter(slug__iexact=company).first()
        if org:
            self.request.session['organizacion_id'] = org.id
        return redirect(self.get_success_url())

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return reverse('admin_inicio')
        elif user.groups.filter(name='cajeros').exists():
            return reverse('facturas:facturar')
        else:
            return reverse('inicio')

# --- Panel de administración con estadísticas ---
@login_required
def panel_administracion(request):
    mes_actual = timezone.now().month
    org = getattr(request, 'organizacion', None)

    # If there's an active organization (tenant), scope the dashboard to it.
    if org is not None:
        total_clientes = Cliente.objects.filter(organizacion=org).count()
        total_productos = Producto.objects.filter(organizacion=org).count()
        total_categorias = Categoria.objects.count()
        total_facturas = Factura.objects.filter(organizacion=org).count()
        nuevos_clientes = Cliente.objects.filter(organizacion=org, fecha_registro__month=mes_actual).count()
        productos_bajo_stock = Producto.objects.filter(organizacion=org, stock__lt=10).count()
        ventas_mes_actual = Factura.objects.filter(organizacion=org, fecha__month=mes_actual).count()
        ingresos_mes_actual = Factura.objects.filter(organizacion=org, fecha__month=mes_actual).aggregate(Sum('total'))['total__sum'] or 0
        facturas_pendientes = Factura.objects.filter(organizacion=org, estado='pendiente').count()
        actividad_reciente = Actividad.objects.filter(usuario__organizaciones__organizacion=org).order_by('-fecha')[:5]
    else:
        total_clientes = Cliente.objects.count()
        total_productos = Producto.objects.count()
        total_categorias = Categoria.objects.count()
        total_facturas = Factura.objects.count()
        nuevos_clientes = Cliente.objects.filter(fecha_registro__month=mes_actual).count()
        productos_bajo_stock = Producto.objects.filter(stock__lt=10).count()
        ventas_mes_actual = Factura.objects.filter(fecha__month=mes_actual).count()
        ingresos_mes_actual = Factura.objects.filter(fecha__month=mes_actual).aggregate(Sum('total'))['total__sum'] or 0
        facturas_pendientes = Factura.objects.filter(estado='pendiente').count()
        actividad_reciente = Actividad.objects.all().order_by('-fecha')[:5]

    context = {
        'total_clientes': total_clientes,
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_facturas': total_facturas,
        'nuevos_clientes': nuevos_clientes,
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_mes_actual': ventas_mes_actual,
        'ingresos_mes_actual': ingresos_mes_actual,
        'facturas_pendientes': facturas_pendientes,
        'actividad_reciente': actividad_reciente,
    }
    return render(request, 'dashboard/dashboard.html', context)

# --- Datos para gráficas del dashboard ---
@login_required
def dashboard_data(request):
    data = {
        'nuevos_clientes': 10,
        'ventas_mes': 5000,
        'productos_bajos_stock': 3
    }
    return JsonResponse(data)

# --- Lista de actividad ---
@login_required
def actividad_list(request):
    org = getattr(request, 'organizacion', None)
    if org is not None:
        actividades = Actividad.objects.filter(usuario__organizaciones__organizacion=org).order_by('-fecha')
    else:
        actividades = Actividad.objects.all().order_by('-fecha')
    return render(request, 'core/actividad_list.html', {'actividades': actividades})

def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        formset = CodigoProductoFormSet(request.POST, queryset=CodigoProducto.objects.none())
        if form.is_valid() and formset.is_valid():
            producto = form.save()
            for codigo_form in formset:
                if codigo_form.cleaned_data and not codigo_form.cleaned_data.get('DELETE', False):
                    codigo = codigo_form.save(commit=False)
                    codigo.producto = producto
                    codigo.save()
            return redirect('producto_list')
    else:
        form = ProductoForm()
        formset = CodigoProductoFormSet(queryset=CodigoProducto.objects.none())
    return render(request, 'core/producto_form.html', {'form': form, 'formset': formset})