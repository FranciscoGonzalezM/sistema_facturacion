# views.py (corregido)
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView

# Importar modelos desde la app actual
from .models import Producto, CodigoProducto, Moneda, ConfiguracionTienda
from categorias.models import Categoria

# Importar modelos externos
from proveedores.models import Proveedor

# Importar TODOS los formularios necesarios
from .forms import ProductoForm, CodigoProductoFormSet, MonedaForm, ConfiguracionTiendaForm



# Listar productos (sin cambios importantes)
def producto_list(request):
    search_query = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    proveedor_id = request.GET.get('proveedor', '')
    stock_filter = request.GET.get('stock', '')
    moneda_id = request.GET.get('moneda', '')
    estado = request.GET.get('estado', '')
    
    org = getattr(request, 'organizacion', None)
    productos = Producto.objects.filter(organizacion=org) if org is not None else Producto.objects.all()
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) |
            Q(codigos__codigo_barra__icontains=search_query) |
            Q(codigos__codigo_qr__icontains=search_query)
        ).distinct()
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if proveedor_id:
        productos = productos.filter(proveedor_id=proveedor_id)
    if moneda_id:
        productos = productos.filter(moneda_id=moneda_id)
    if estado:
        if estado == 'activo':
            productos = productos.filter(activo=True)
        elif estado == 'inactivo':
            productos = productos.filter(activo=False)
    if stock_filter:
        if stock_filter == 'bajo':
            productos = productos.filter(stock__lt=10)
        elif stock_filter == 'medio':
            productos = productos.filter(stock__gte=10, stock__lt=50)
        elif stock_filter == 'alto':
            productos = productos.filter(stock__gte=50)
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categorias = Categoria.objects.all()
    org = getattr(request, 'organizacion', None)
    proveedores = Proveedor.objects.filter(organizacion=org, estado='activo') if org is not None else Proveedor.objects.filter(estado='activo')
    monedas = Moneda.objects.all()
    # Estadísticas rápidas usadas en la plantilla (scope por organización)
    total_productos = Producto.objects.filter(organizacion=org).count() if org is not None else Producto.objects.count()
    productos_activos = Producto.objects.filter(organizacion=org, activo=True).count() if org is not None else Producto.objects.filter(activo=True).count()
    stock_bajo_count = Producto.objects.filter(organizacion=org, stock__lt=10).count() if org is not None else Producto.objects.filter(stock__lt=10).count()
    total_monedas = monedas.count()
    context = {
        'productos': page_obj,
        'categorias': categorias,
        'proveedores': proveedores,
        'monedas': monedas,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'stock_bajo_count': stock_bajo_count,
        'total_monedas': total_monedas,
    }
    return render(request, 'core/producto_list.html', context)

# Crear producto con múltiples códigos (corregido)
@login_required
def producto_create(request):
    formset_prefix = 'codigos'
    org = getattr(request, 'organizacion', None)
    # Allow staff or organization owner/admin
    if not (request.user.is_staff or (org is not None and request.user.organizaciones.filter(organizacion=org, role__in=['owner','admin']).exists())):
        raise PermissionDenied()
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        # Validamos el producto primero
        if form.is_valid():
            producto = form.save(commit=False)
            org = getattr(request, 'organizacion', None)
            if org is not None:
                producto.organizacion = org
            producto.save()  # guardamos el producto para tener PK
            # Ahora instanciamos el formset ligado al producto (instance) y con prefix
            formset = CodigoProductoFormSet(request.POST, instance=producto, prefix=formset_prefix)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Producto creado exitosamente.')
                return redirect('productos:producto_list')
            else:
                # Mostrar errores del formset
                messages.error(request, 'Corrige los errores en los códigos.')
        else:
            # Si el form no es válido, instanciamos un formset vacío (para renderizar)
            formset = CodigoProductoFormSet(prefix=formset_prefix)
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm()
        formset = CodigoProductoFormSet(prefix=formset_prefix)
    return render(request, 'core/producto_form.html', {'form': form, 'formset': formset})
def obtener_monedas(request):
    monedas = Moneda.objects.all()
    return render(request, 'monedas/lista.html', {'monedas': monedas})

# Editar producto con múltiples códigos (corregido)
@login_required
def producto_edit(request, pk):
    org = getattr(request, 'organizacion', None)
    producto = get_object_or_404(Producto.objects.filter(organizacion=org) if org is not None else Producto.objects, pk=pk)
    # Permission: staff or owner/admin of the organization
    if not (request.user.is_staff or (org is not None and request.user.organizaciones.filter(organizacion=org, role__in=['owner','admin']).exists())):
        raise PermissionDenied()
    formset_prefix = 'codigos'
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        formset = CodigoProductoFormSet(request.POST, instance=producto, prefix=formset_prefix)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('productos:producto_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm(instance=producto)
        formset = CodigoProductoFormSet(instance=producto, prefix=formset_prefix)
    return render(request, 'core/producto_form.html', {'form': form, 'formset': formset})

# Eliminar producto
@login_required
def producto_delete(request, pk):
    org = getattr(request, 'organizacion', None)
    producto = get_object_or_404(Producto.objects.filter(organizacion=org) if org is not None else Producto.objects, pk=pk)
    # Permission: staff or owner/admin of the organization
    if not (request.user.is_staff or (org is not None and request.user.organizaciones.filter(organizacion=org, role__in=['owner','admin']).exists())):
        raise PermissionDenied()
    if request.method == "POST":
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('productos:producto_list')
    return render(request, 'core/producto_confirm_delete.html', {'object': producto})

# Búsqueda rápida para facturación - Busca por código de barras o QR
def buscar_producto_por_codigo(request):
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({'error': 'Código no proporcionado'}, status=400)
    
    try:
        # Buscar el código en los códigos de barras o QR, respetando organización
        org = getattr(request, 'organizacion', None)
        codigo_qs = CodigoProducto.objects.filter(Q(codigo_barra=codigo) | Q(codigo_qr=codigo))
        if org is not None:
            codigo_qs = codigo_qs.filter(producto__organizacion=org)
        codigo_producto = codigo_qs.select_related('producto').get()
        
        producto = codigo_producto.producto
        
        # Verificar si el producto está activo y tiene stock
        if not producto.activo:
            return JsonResponse({'error': 'Producto inactivo'}, status=400)
            
        if producto.stock <= 0:
            return JsonResponse({'error': 'Producto sin stock'}, status=400)
        
        # Devolver datos del producto (incluyendo información del proveedor)
        data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'stock': producto.stock,
            'categoria': producto.categoria.nombre,
            'proveedor': producto.proveedor.nombre_empresa if producto.proveedor else 'Sin proveedor',  # Info del proveedor
            'proveedor_id': producto.proveedor.id if producto.proveedor else None,
            'codigo_barra': codigo_producto.codigo_barra,
            'codigo_qr': codigo_producto.codigo_qr
        }
        
        return JsonResponse(data)
        
    except CodigoProducto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Listar productos por proveedor específico
def productos_por_proveedor(request, proveedor_id):
    org = getattr(request, 'organizacion', None)
    proveedor = get_object_or_404(Proveedor.objects.filter(organizacion=org) if org is not None else Proveedor.objects, id=proveedor_id)
    productos = Producto.objects.filter(proveedor=proveedor)
    
    # Obtener parámetros de filtrado
    search_query = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    stock_filter = request.GET.get('stock', '')
    
    if search_query:
        productos = productos.filter(
            Q(nombre__icontains=search_query) |
            Q(codigos__codigo_barra__icontains=search_query) |
            Q(codigos__codigo_qr__icontains=search_query)
        ).distinct()
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if stock_filter:
        if stock_filter == 'bajo':
            productos = productos.filter(stock__lt=10)
        elif stock_filter == 'medio':
            productos = productos.filter(stock__gte=10, stock__lt=50)
        elif stock_filter == 'alto':
            productos = productos.filter(stock__gte=50)
    
    # Paginación
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categorias = Categoria.objects.all()
    
    context = {
        'productos': page_obj,
        'proveedor': proveedor,
        'categorias': categorias,
    }
    
    return render(request, 'core/productos_por_proveedor.html', context)

@login_required
def lista_monedas(request):
    monedas = Moneda.objects.all()
    config = ConfiguracionTienda.objects.first()
    return render(request, 'core/lista_monedas.html', {
        'monedas': monedas,
        'config': config
    })

@login_required
def crear_moneda(request):
    if request.method == 'POST':
        form = MonedaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Moneda creada exitosamente.')
            return redirect('productos:lista_monedas')
    else:
        form = MonedaForm()
    
    return render(request, 'core/moneda_form.html', {'form': form})

@login_required
def editar_moneda(request, pk):
    moneda = get_object_or_404(Moneda, pk=pk)
    if request.method == 'POST':
        form = MonedaForm(request.POST, instance=moneda)
        if form.is_valid():
            form.save()
            messages.success(request, 'Moneda actualizada exitosamente.')
            return redirect('productos:lista_monedas')
    else:
        form = MonedaForm(instance=moneda)
    
    return render(request, 'core/moneda_form.html', {'form': form})

@login_required
def configurar_tienda(request):
    config = ConfiguracionTienda.objects.first()
    if not config:
        # Crear configuración por defecto si no existe
        moneda_principal = Moneda.objects.filter(principal=True).first()
        if not moneda_principal:
            moneda_principal = Moneda.objects.first()
        config = ConfiguracionTienda.objects.create(moneda_principal=moneda_principal)
    
    if request.method == 'POST':
        form = ConfiguracionTiendaForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración de tienda actualizada.')
            return redirect('productos:lista_monedas')
    else:
        form = ConfiguracionTiendaForm(instance=config)
    
    return render(request, 'core/config_tienda_form.html', {'form': form})

# Vista actualizada de lista_productos con estadísticas
@login_required
def lista_productos(request):
    org = getattr(request, 'organizacion', None)
    productos = Producto.all_objects.all().select_related('categoria', 'proveedor', 'moneda').prefetch_related('codigos')
    if org is not None:
        productos = productos.filter(organizacion=org)
    
    # Aplicar filtros
    search = request.GET.get('search', '')
    categoria_id = request.GET.get('categoria', '')
    moneda_id = request.GET.get('moneda', '')
    stock_filter = request.GET.get('stock', '')
    estado_filter = request.GET.get('estado', '')
    
    if search:
        productos = productos.filter(nombre__icontains=search)
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if moneda_id:
        productos = productos.filter(moneda_id=moneda_id)
    
    if stock_filter:
        if stock_filter == 'bajo':
            productos = productos.filter(stock__lt=10)
        elif stock_filter == 'medio':
            productos = productos.filter(stock__range=[10, 50])
        elif stock_filter == 'alto':
            productos = productos.filter(stock__gt=50)
    
    if estado_filter:
        if estado_filter == 'activo':
            productos = productos.filter(activo=True)
        elif estado_filter == 'inactivo':
            productos = productos.filter(activo=False)
    
    # Estadísticas para el template (scoped)
    total_products_qs = Producto.all_objects.filter(organizacion=org) if org is not None else Producto.all_objects
    total_productos = total_products_qs.count()
    productos_activos = Producto.objects.filter(organizacion=org).count() if org is not None else Producto.objects.count()
    stock_bajo_count = total_products_qs.filter(stock__lt=10).count()
    total_monedas = Moneda.objects.count()
    
    # Paginación
    paginator = Paginator(productos, 20)
    page = request.GET.get('page')
    try:
        productos = paginator.page(page)
    except PageNotAnInteger:
        productos = paginator.page(1)
    except EmptyPage:
        productos = paginator.page(paginator.num_pages)
    
    context = {
        'productos': productos,
        'categorias': Categoria.objects.all(),
        'monedas': Moneda.objects.all(),
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'stock_bajo_count': stock_bajo_count,
        'total_monedas': total_monedas,
    }
    
    return render(request, 'core/lista_productos.html', context)