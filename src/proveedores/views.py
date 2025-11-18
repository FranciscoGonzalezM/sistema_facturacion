from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Proveedor, ContactoProveedor, PedidoProveedor, ItemPedido
from .forms import ProveedorForm, ContactoProveedorForm, PedidoProveedorForm, ItemPedidoForm
from productos.models import Producto


class TenantMixin:
    def get_organizacion(self):
        return getattr(self.request, 'organizacion', None)

    def filter_by_organizacion(self, queryset):
        org = self.get_organizacion()
        if org is not None:
            return queryset.filter(organizacion=org)
        return queryset

class ProveedorListView(TenantMixin, LoginRequiredMixin, ListView):
    model = Proveedor
    template_name = 'core/proveedor_list.html'
    context_object_name = 'proveedores'
    paginate_by = 10
    # Scope lists to tenant
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_by_organizacion(queryset)
        # Filtros
        search_query = self.request.GET.get('search', '')
        estado_filter = self.request.GET.get('estado', '')
        tipo_filter = self.request.GET.get('tipo', '')

        if search_query:
            queryset = queryset.filter(
                Q(nombre_empresa__icontains=search_query) |
                Q(nombre_contacto__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(ciudad__icontains=search_query) |
                Q(rfc__icontains=search_query)
            )

        if estado_filter:
            queryset = queryset.filter(estado=estado_filter)

        if tipo_filter:
            queryset = queryset.filter(tipo_proveedor=tipo_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Proveedor.ESTADO_CHOICES
        context['tipos_proveedor'] = Proveedor.TIPO_PROVEEDOR
        return context

class ProveedorDetailView(TenantMixin, LoginRequiredMixin, DetailView):
    model = Proveedor
    template_name = 'core/proveedor_detail.html'
    context_object_name = 'proveedor'

    def get_queryset(self):
        return self.filter_by_organizacion(super().get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contactos'] = self.object.contactos.all()
        context['pedidos'] = self.object.pedidos.all().order_by('-fecha_pedido')[:5]

        # Obtener productos relacionados con este proveedor (scope by tenant when present)
        org = getattr(self.request, 'organizacion', None)
        productos_qs = Producto.objects.filter(proveedor=self.object)
        if org is not None:
            productos_qs = productos_qs.filter(organizacion=org)
        context['productos'] = productos_qs
        
        # Estadísticas
        context['total_productos'] = context['productos'].count()
        context['productos_activos'] = context['productos'].filter(activo=True).count()
        context['productos_bajo_stock'] = context['productos'].filter(stock__lt=10).count()
        
        return context

class ProveedorCreateView(TenantMixin, LoginRequiredMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'core/proveedor_form.html'
    success_url = reverse_lazy('proveedores:lista')

    def form_valid(self, form):
        org = getattr(self.request, 'organizacion', None)
        if org is not None:
            form.instance.organizacion = org
        messages.success(self.request, 'Proveedor creado exitosamente.')
        return super().form_valid(form)

class ProveedorUpdateView(TenantMixin, LoginRequiredMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'core/proveedor_form.html'
    success_url = reverse_lazy('proveedores:lista')

    def get_queryset(self):
        return self.filter_by_organizacion(super().get_queryset())

    def form_valid(self, form):
        org = getattr(self.request, 'organizacion', None)
        if org is not None:
            form.instance.organizacion = org
        messages.success(self.request, 'Proveedor actualizado exitosamente.')
        return super().form_valid(form)

class ProveedorDeleteView(TenantMixin, LoginRequiredMixin, DeleteView):
    model = Proveedor
    template_name = 'core/proveedor_confirm_delete.html'
    success_url = reverse_lazy('proveedores:lista')

    def get_queryset(self):
        return self.filter_by_organizacion(super().get_queryset())

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Proveedor eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

# Vistas para Contactos
class ContactoCreateView(LoginRequiredMixin, CreateView):
    model = ContactoProveedor
    form_class = ContactoProveedorForm
    template_name = 'core/contacto_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['proveedor'] = self.kwargs['proveedor_id']
        return initial

    def form_valid(self, form):
        proveedor_id = self.kwargs['proveedor_id']
        org = getattr(self.request, 'organizacion', None)
        proveedor = get_object_or_404(Proveedor.objects.filter(organizacion=org) if org is not None else Proveedor.objects, pk=proveedor_id)
        form.instance.proveedor = proveedor
        messages.success(self.request, 'Contacto agregado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle', kwargs={'pk': self.kwargs['proveedor_id']})

class ContactoUpdateView(LoginRequiredMixin, UpdateView):
    model = ContactoProveedor
    form_class = ContactoProveedorForm
    template_name = 'core/contacto_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Contacto actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle', kwargs={'pk': self.object.proveedor.id})

class ContactoDeleteView(LoginRequiredMixin, DeleteView):
    model = ContactoProveedor
    template_name = 'core/contacto_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        contacto = self.get_object()
        proveedor_id = contacto.proveedor.id
        messages.success(request, 'Contacto eliminado exitosamente.')
        response = super().delete(request, *args, **kwargs)
        return response

    def get_success_url(self):
        contacto = self.get_object()
        return reverse_lazy('proveedores:detalle', kwargs={'pk': contacto.proveedor.id})

# Vistas para Pedidos
class PedidoCreateView(TenantMixin, LoginRequiredMixin, CreateView):
    model = PedidoProveedor
    form_class = PedidoProveedorForm
    template_name = 'core/pedido_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedor_id = self.kwargs.get('proveedor_id')
        context['proveedor_id'] = proveedor_id
        org = getattr(self.request, 'organizacion', None)
        context['proveedor'] = get_object_or_404(Proveedor.objects.filter(organizacion=org) if org is not None else Proveedor.objects, pk=proveedor_id)
        return context

    def form_valid(self, form):
        proveedor_id = self.kwargs.get('proveedor_id')
        org = getattr(self.request, 'organizacion', None)
        form.instance.proveedor = get_object_or_404(Proveedor.objects.filter(organizacion=org) if org is not None else Proveedor.objects, pk=proveedor_id)
        form.instance.estado = 'pendiente'
        form.instance.total = 0
        messages.success(self.request, 'Pedido creado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle_pedido', kwargs={'pk': self.object.pk})

class PedidoDetailView(TenantMixin, LoginRequiredMixin, DetailView):
    model = PedidoProveedor
    template_name = 'core/pedido_detail.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        return self.filter_by_organizacion(super().get_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

class PedidoUpdateView(TenantMixin, LoginRequiredMixin, UpdateView):
    model = PedidoProveedor
    form_class = PedidoProveedorForm
    template_name = 'core/pedido_form.html'

    def get_queryset(self):
        return self.filter_by_organizacion(super().get_queryset())

    def form_valid(self, form):
        messages.success(self.request, 'Pedido actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle_pedido', kwargs={'pk': self.object.pk})

class PedidoDeleteView(TenantMixin, LoginRequiredMixin, DeleteView):
    model = PedidoProveedor
    template_name = 'core/pedido_confirm_delete.html'

    def get_queryset(self):
        return TenantMixin().filter_by_organizacion(super().get_queryset())

    def delete(self, request, *args, **kwargs):
        pedido = self.get_object()
        proveedor_id = pedido.proveedor.id
        messages.success(request, 'Pedido eliminado exitosamente.')
        response = super().delete(request, *args, **kwargs)
        return response

    def get_success_url(self):
        pedido = self.get_object()
        return reverse_lazy('proveedores:detalle', kwargs={'pk': pedido.proveedor.id})

# Vistas para Items de Pedido
class ItemPedidoCreateView(LoginRequiredMixin, CreateView):
    model = ItemPedido
    form_class = ItemPedidoForm
    template_name = 'core/itempedido_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['pedido'] = self.kwargs['pedido_id']
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        pedido_id = self.kwargs.get('pedido_id')
        org = getattr(self.request, 'organizacion', None)
        pedido = get_object_or_404(PedidoProveedor.objects.filter(organizacion=org) if org is not None else PedidoProveedor.objects, pk=pedido_id)
        kwargs['proveedor_id'] = pedido.proveedor.id
        return kwargs

    def form_valid(self, form):
        form.instance.pedido_id = self.kwargs['pedido_id']
        messages.success(self.request, 'Item agregado al pedido exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proveedores:detalle_pedido', kwargs={'pk': self.kwargs['pedido_id']})

class ItemPedidoUpdateView(LoginRequiredMixin, UpdateView):
    model = ItemPedido
    form_class = ItemPedidoForm
    template_name = 'core/itempedido_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        item = self.get_object()
        kwargs['proveedor_id'] = item.pedido.proveedor.id
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Item actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        item = self.get_object()
        return reverse_lazy('proveedores:detalle_pedido', kwargs={'pk': item.pedido.id})

class ItemPedidoDeleteView(LoginRequiredMixin, DeleteView):
    model = ItemPedido
    template_name = 'core/itempedido_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        pedido_id = item.pedido.id
        messages.success(request, 'Item eliminado del pedido exitosamente.')
        response = super().delete(request, *args, **kwargs)
        return response

    def get_success_url(self):
        item = self.get_object()
        return reverse_lazy('proveedores:detalle_pedido', kwargs={'pk': item.pedido.id})

# Búsqueda de proveedores
def buscar_proveedores(request):
    query = request.GET.get('q', '')
    estado_filter = request.GET.get('estado', '')
    tipo_filter = request.GET.get('tipo', '')
    
    org = getattr(request, 'organizacion', None)
    proveedores = Proveedor.objects.filter(organizacion=org) if org is not None else Proveedor.objects.all()
    
    if query:
        proveedores = proveedores.filter(
            Q(nombre_empresa__icontains=query) |
            Q(nombre_contacto__icontains=query) |
            Q(email__icontains=query) |
            Q(ciudad__icontains=query) |
            Q(rfc__icontains=query)
        )
    
    if estado_filter:
        proveedores = proveedores.filter(estado=estado_filter)
    
    if tipo_filter:
        proveedores = proveedores.filter(tipo_proveedor=tipo_filter)
    
    return render(request, 'core/proveedor_list.html', {
        'proveedores': proveedores,
        'query': query,
        'estado_filter': estado_filter,
        'tipo_filter': tipo_filter,
        'estados': Proveedor.ESTADO_CHOICES,
        'tipos_proveedor': Proveedor.TIPO_PROVEEDOR
    })

# Vista para dashboard de proveedor
def proveedor_dashboard(request, pk):
    org = getattr(request, 'organizacion', None)
    proveedor = get_object_or_404(Proveedor.objects.filter(organizacion=org) if org is not None else Proveedor.objects, pk=pk)
    
    # Estadísticas
    productos_qs = Producto.objects.filter(proveedor=proveedor)
    if org is not None:
        productos_qs = productos_qs.filter(organizacion=org)

    total_productos = productos_qs.count()
    productos_activos = productos_qs.filter(activo=True).count()
    productos_bajo_stock = productos_qs.filter(stock__lt=10).count()

    # Últimos productos
    ultimos_productos = productos_qs.order_by('-id')[:5]

    # Últimos pedidos (scoped by proveedor; pedidos are linked to proveedor)
    ultimos_pedidos = PedidoProveedor.objects.filter(proveedor=proveedor).order_by('-fecha_pedido')[:5]
    
    context = {
        'proveedor': proveedor,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_bajo_stock': productos_bajo_stock,
        'ultimos_productos': ultimos_productos,
        'ultimos_pedidos': ultimos_pedidos,
    }
    
    return render(request, 'core/proveedor_dashboard.html', context)