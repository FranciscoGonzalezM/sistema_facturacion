from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from .models import Articulo, CodigoArticulo, Moneda, ConfiguracionTienda
from categorias.models import Categoria
from proveedores.models import Proveedor
from .forms import ArticuloForm, CodigoArticuloFormSet, MonedaForm, ConfiguracionTiendaForm


def _get_organizacion(request):
    return getattr(request, 'organizacion', None)


def _has_permission(request, org):
    """Verificar si el usuario tiene permisos de admin/owner"""
    if request.user.is_staff:
        return True
    if org is not None:
        return request.user.organizaciones.filter(
            organizacion=org, 
            role__in=['owner', 'admin']
        ).exists()
    return False


@login_required
def articulo_list(request):
    """Listar artículos con filtros y paginación"""
    search_query = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    proveedor_id = request.GET.get('proveedor', '')
    stock_filter = request.GET.get('stock', '')
    moneda_id = request.GET.get('moneda', '')
    estado = request.GET.get('estado', '')
    
    org = _get_organizacion(request)
    articulos = Articulo.objects.filter(organizacion=org) if org else Articulo.objects.all()
    
    if search_query:
        articulos = articulos.filter(
            Q(nombre__icontains=search_query) |
            Q(codigos__codigo_barra__icontains=search_query) |
            Q(codigos__codigo_qr__icontains=search_query)
        ).distinct()
    
    if categoria_id:
        articulos = articulos.filter(categoria_id=categoria_id)
    if proveedor_id:
        articulos = articulos.filter(proveedor_id=proveedor_id)
    if moneda_id:
        articulos = articulos.filter(moneda_id=moneda_id)
    if estado:
        if estado == 'activo':
            articulos = articulos.filter(activo=True)
        elif estado == 'inactivo':
            articulos = articulos.filter(activo=False)
    if stock_filter:
        if stock_filter == 'bajo':
            articulos = articulos.filter(stock__lt=10)
        elif stock_filter == 'medio':
            articulos = articulos.filter(stock__gte=10, stock__lt=50)
        elif stock_filter == 'alto':
            articulos = articulos.filter(stock__gte=50)
    
    paginator = Paginator(articulos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.filter(organizacion=org, estado='activo') if org else Proveedor.objects.filter(estado='activo')
    monedas = Moneda.objects.all()
    
    # Estadísticas
    total_articulos = Articulo.objects.filter(organizacion=org).count() if org else Articulo.objects.count()
    articulos_activos = Articulo.objects.filter(organizacion=org, activo=True).count() if org else Articulo.objects.filter(activo=True).count()
    stock_bajo_count = Articulo.objects.filter(organizacion=org, stock__lt=10).count() if org else Articulo.objects.filter(stock__lt=10).count()
    
    context = {
        'articulos': page_obj,
        'categorias': categorias,
        'proveedores': proveedores,
        'monedas': monedas,
        'total_articulos': total_articulos,
        'articulos_activos': articulos_activos,
        'stock_bajo_count': stock_bajo_count,
        'total_monedas': monedas.count(),
    }
    return render(request, 'articulos/articulo_list.html', context)


@login_required
def articulo_create(request):
    """Crear nuevo artículo"""
    org = _get_organizacion(request)
    
    if not _has_permission(request, org):
        raise PermissionDenied()
    
    formset_prefix = 'codigos'
    
    if request.method == 'POST':
        form = ArticuloForm(request.POST)
        if form.is_valid():
            articulo = form.save(commit=False)
            if org:
                articulo.organizacion = org
            articulo.save()
            
            formset = CodigoArticuloFormSet(request.POST, instance=articulo, prefix=formset_prefix)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Artículo creado exitosamente.')
                return redirect('articulos:articulo_list')
            else:
                messages.error(request, 'Corrige los errores en los códigos.')
        else:
            formset = CodigoArticuloFormSet(prefix=formset_prefix)
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ArticuloForm()
        formset = CodigoArticuloFormSet(prefix=formset_prefix)
    
    return render(request, 'articulos/articulo_form.html', {'form': form, 'formset': formset})


@login_required
def articulo_edit(request, pk):
    """Editar artículo existente"""
    org = _get_organizacion(request)
    articulo = get_object_or_404(
        Articulo.objects.filter(organizacion=org) if org else Articulo.objects, 
        pk=pk
    )
    
    if not _has_permission(request, org):
        raise PermissionDenied()
    
    formset_prefix = 'codigos'
    
    if request.method == 'POST':
        form = ArticuloForm(request.POST, instance=articulo)
        formset = CodigoArticuloFormSet(request.POST, instance=articulo, prefix=formset_prefix)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Artículo actualizado exitosamente.')
            return redirect('articulos:articulo_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ArticuloForm(instance=articulo)
        formset = CodigoArticuloFormSet(instance=articulo, prefix=formset_prefix)
    
    return render(request, 'articulos/articulo_form.html', {'form': form, 'formset': formset, 'articulo': articulo})


@login_required
def articulo_delete(request, pk):
    """Eliminar artículo"""
    org = _get_organizacion(request)
    articulo = get_object_or_404(
        Articulo.objects.filter(organizacion=org) if org else Articulo.objects, 
        pk=pk
    )
    
    if not _has_permission(request, org):
        raise PermissionDenied()
    
    if request.method == "POST":
        articulo.delete()
        messages.success(request, 'Artículo eliminado exitosamente.')
        return redirect('articulos:articulo_list')
    
    return render(request, 'articulos/articulo_confirm_delete.html', {'articulo': articulo})


def buscar_articulo_por_codigo(request):
    """API para buscar artículo por código de barras o QR"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({'error': 'Código no proporcionado'}, status=400)
    
    try:
        org = _get_organizacion(request)
        codigo_qs = CodigoArticulo.objects.filter(
            Q(codigo_barra=codigo) | Q(codigo_qr=codigo)
        )
        if org:
            codigo_qs = codigo_qs.filter(articulo__organizacion=org)
        
        codigo_articulo = codigo_qs.select_related('articulo').get()
        articulo = codigo_articulo.articulo
        
        if not articulo.activo:
            return JsonResponse({'error': 'Artículo inactivo'}, status=400)
        
        if articulo.stock <= 0:
            return JsonResponse({'error': 'Artículo sin stock'}, status=400)
        
        data = {
            'id': articulo.id,
            'nombre': articulo.nombre,
            'precio': str(articulo.precio),
            'stock': articulo.stock,
            'categoria': articulo.categoria.nombre,
            'proveedor': articulo.proveedor.nombre_empresa if articulo.proveedor else 'Sin proveedor',
            'codigo_barra': codigo_articulo.codigo_barra,
            'codigo_qr': codigo_articulo.codigo_qr
        }
        return JsonResponse(data)
        
    except CodigoArticulo.DoesNotExist:
        return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def lista_monedas(request):
    """Listar monedas"""
    monedas = Moneda.objects.all()
    config = ConfiguracionTienda.objects.first()
    return render(request, 'articulos/lista_monedas.html', {
        'monedas': monedas,
        'config': config
    })


@login_required
def crear_moneda(request):
    """Crear nueva moneda"""
    if request.method == 'POST':
        form = MonedaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Moneda creada exitosamente.')
            return redirect('articulos:lista_monedas')
    else:
        form = MonedaForm()
    
    return render(request, 'articulos/moneda_form.html', {'form': form})


@login_required
def editar_moneda(request, pk):
    """Editar moneda existente"""
    moneda = get_object_or_404(Moneda, pk=pk)
    
    if request.method == 'POST':
        form = MonedaForm(request.POST, instance=moneda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Moneda actualizada exitosamente.')
            return redirect('articulos:lista_monedas')
    else:
        form = MonedaForm(instance=moneda)
    
    return render(request, 'articulos/moneda_form.html', {'form': form})


@login_required
def configurar_tienda(request):
    """Configurar tienda"""
    config = ConfiguracionTienda.objects.first()
    if not config:
        moneda_principal = Moneda.objects.filter(principal=True).first()
        if not moneda_principal:
            moneda_principal = Moneda.objects.first()
        if moneda_principal:
            config = ConfiguracionTienda.objects.create(moneda_principal=moneda_principal)
    
    if request.method == 'POST':
        form = ConfiguracionTiendaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de tienda actualizada.')
            return redirect('articulos:lista_monedas')
    else:
        form = ConfiguracionTiendaForm(instance=config)
    
    return render(request, 'articulos/config_tienda_form.html', {'form': form})


