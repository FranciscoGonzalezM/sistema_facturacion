# facturas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import localtime
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.conf import settings

from decimal import Decimal
import json
import os

from productos.models import Producto
from clientes.models import Cliente
from .models import Factura, DetalleFactura
from .forms import FacturaForm, DetalleFacturaFormSet

# NOTE: ReportLab imports moved to lazy imports inside `factura_pdf`
# because reportlab is an optional heavy dependency used only when
# generating PDFs. Importing it at module import time made the
# whole Django process fail if reportlab wasn't installed in the
# active virtualenv. See `factura_pdf` where the real imports occur.

import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt




# ---- Funciones de permisos ----
def es_admin_o_vendedor(user):
    """Verifica si el usuario es admin o pertenece a grupos de vendedores/cajeros"""
    # Allow staff, group-based sellers, or organization members with owner/admin role
    try:
        org_member = getattr(user, 'organizaciones', None) and user.organizaciones.filter(role__in=['owner', 'admin', 'cajero']).exists()
    except Exception:
        org_member = False
    return user.is_staff or user.groups.filter(name__in=['Vendedores', 'cajeros']).exists() or org_member

def es_vendedor(user):
    """Verifica si el usuario es vendedor o cajero"""
    # Allow staff, cajeros group, or organization owner/admin to act as vendedor
    try:
        org_member = getattr(user, 'organizaciones', None) and user.organizaciones.filter(role__in=['owner', 'admin', 'cajero']).exists()
    except Exception:
        org_member = False
    return user.is_staff or user.groups.filter(name='cajeros').exists() or org_member

# ---- Vista principal de facturación ----
@login_required(login_url='/login/')
@user_passes_test(es_vendedor)
@transaction.atomic
def facturar(request):
    org = getattr(request, 'organizacion', None)
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        print("POST data:", dict(request.POST))  # 👀 solo debug, quítalo en producción

        # ----------------------------
        # Manejo de código de barra
        # ----------------------------
        productos_data = []
        codigo_barra = request.POST.get('codigo_barra')

        if codigo_barra:
            try:
                if org is not None:
                    producto = Producto.objects.get(codigo_barra=codigo_barra, activo=True, organizacion=org)
                else:
                    producto = Producto.objects.get(codigo_barra=codigo_barra, activo=True)
                if producto.stock <= 0:
                    messages.error(request, f"❌ El producto '{producto.nombre}' no tiene stock disponible.")
                    return redirect('facturas:facturar')

                productos_data = [{
                    "id": producto.id,
                    "cantidad": 1,  # ⚠️ ahora siempre 1, puedes cambiar a dinámico si quieres
                    "precio": float(producto.precio),
                    "moneda": producto.moneda.id,
                    "iva": True
                }]

            except Producto.DoesNotExist:
                messages.error(request, f"❌ No se encontró producto con código de barras {codigo_barra}")
                return redirect('facturas:facturar')

        # ----------------------------
        # Validación del formulario
        # ----------------------------
        if form.is_valid():
            try:
                # Crear factura en memoria
                factura = form.save(commit=False)
                if org is not None:
                    factura.organizacion = org
                factura.usuario = request.user
                factura.metodo_pago = request.POST.get('metodo_pago', 'efectivo')
                factura.id_transaccion = request.POST.get('id_transaccion', '')
                factura.estado_pago = request.POST.get('estado_pago', 'pendiente')

                # Pagos en efectivo
                if factura.metodo_pago == 'efectivo':
                    try:
                        factura.monto_recibido = Decimal(request.POST.get('monto_recibido', '0'))
                        factura.vuelto = Decimal(request.POST.get('vuelto', '0'))
                    except (ValueError, Exception):
                        factura.monto_recibido = Decimal('0')
                        factura.vuelto = Decimal('0')

                    factura.pagada = True
                    factura.estado_pago = 'completado'

                factura.save()

                # ----------------------------
                # Procesar productos
                # ----------------------------
                if not productos_data:
                    productos_json = request.POST.get('productos_json')
                    if not productos_json:
                        raise ValidationError('No se encontraron productos en la factura')
                    productos_data = json.loads(productos_json)

                ids = [int(p['id']) for p in productos_data]
                productos_qs = Producto.objects.select_related('moneda').filter(id__in=ids)
                if org is not None:
                    productos_qs = productos_qs.filter(organizacion=org)
                productos = {p.id: p for p in productos_qs}

                for prod_data in productos_data:
                    producto = productos.get(int(prod_data['id']))
                    if not producto:
                        raise ValidationError(f'Producto con ID {prod_data["id"]} no existe')

                    cantidad = int(prod_data['cantidad'])
                    if producto.stock < cantidad:
                        raise ValidationError(
                            f'Stock insuficiente para {producto.nombre}. '
                            f'Disponible: {producto.stock}, Solicitado: {cantidad}'
                        )

                    DetalleFactura.objects.create(
                        factura=factura,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=Decimal(str(prod_data['precio'])),
                        moneda=producto.moneda,
                        iva=prod_data.get('iva', True)
                    )

                    # Descontar stock
                    producto.stock -= cantidad
                    producto.save()

                # Recalcular totales
                factura.calcular_totales()
                factura.save()

                messages.success(request, f'Factura #{factura.id} creada correctamente ✅')
                return redirect('facturas:factura_detalle', pk=factura.id)

            except ValidationError as e:
                messages.error(request, str(e))
                raise  # fuerza rollback
            except Exception as e:
                messages.error(request, f'⚠️ Error inesperado al guardar la factura')
                raise  # log real -> logger.error(str(e))

        else:
            messages.error(request, 'Error en los datos del formulario')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    else:
        form = FacturaForm()
        productos_con_moneda = Producto.objects.select_related('moneda').filter(stock__gt=0, activo=True)
        if org is not None:
            productos_con_moneda = productos_con_moneda.filter(organizacion=org)
     
    return render(request, 'core/facturar.html', {
        'form': form,
        'productos': productos_con_moneda,
        'clientes': Cliente.objects.filter(organizacion=org) if org is not None else Cliente.objects.all(),
        'numero_factura': Factura.objects.filter(organizacion=org).count() + 1 if org is not None else Factura.objects.count() + 1
    })
    

# ---- Listado de facturas ----
@login_required
@user_passes_test(es_admin_o_vendedor)
def factura_list(request):
    org = getattr(request, 'organizacion', None)
    facturas = Factura.objects.filter(organizacion=org).order_by('-fecha') if org is not None else Factura.objects.all().order_by('-fecha')
    # Añadir información de moneda por factura (predominante o mezcla)
    for factura in facturas:
        detalles = factura.detalles.all()
        codigos = set(d.moneda.codigo for d in detalles if getattr(d, 'moneda', None))
        simbolos = set((d.moneda.simbolo or '') for d in detalles if getattr(d, 'moneda', None))
        if len(codigos) == 1:
            factura.currency_code = list(codigos)[0]
            # preferir símbolo si existe, sino usar el código
            s = next((d.moneda.simbolo for d in detalles if getattr(d, 'moneda', None) and d.moneda.simbolo), '')
            factura.currency_symbol = s or factura.currency_code
            factura.currency_mixed = False
        elif len(codigos) > 1:
            factura.currency_code = 'MULTI'
            factura.currency_symbol = ''
            factura.currency_mixed = True
        else:
            factura.currency_code = getattr(settings, 'DEFAULT_CURRENCY', 'USD')
            factura.currency_symbol = factura.currency_code
            factura.currency_mixed = False

    return render(request, 'core/factura_list.html', {'facturas': facturas})

@login_required
def factura_detalle(request, pk):
    org = getattr(request, 'organizacion', None)
    factura = get_object_or_404(Factura.objects.filter(organizacion=org) if org is not None else Factura.objects, pk=pk)
    detalles = factura.detalles.all()
    for detalle in detalles:
        if detalle.iva:
            detalle.iva_monto = detalle.subtotal * Decimal('0.15')
        else:
            detalle.iva_monto = Decimal('0.00')
        detalle.total_con_iva = detalle.subtotal + detalle.iva_monto
    return render(request, 'core/factura_detalle.html', {
        'factura': factura,
        'detalles': detalles
    })

# ---- Generar PDF de factura con hora local y QR centrado ----
@login_required
@user_passes_test(es_admin_o_vendedor)
def factura_pdf(request, pk):
    org = getattr(request, 'organizacion', None)
    factura = get_object_or_404(Factura.objects.filter(organizacion=org) if org is not None else Factura.objects, id=pk)
    detalles = factura.detalles.all()
    for detalle in detalles:
        detalle.iva_monto = detalle.subtotal * Decimal('0.19') if detalle.iva else Decimal('0.00')
        detalle.total_con_iva = detalle.subtotal + detalle.iva_monto

    # IMPORTS PEREZOSOS: importar ReportLab solo cuando se genera el PDF
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.units import cm, inch
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib import colors
        from reportlab.graphics.barcode import qr
        from reportlab.graphics.shapes import Drawing
    except Exception:
        # Si reportlab no está disponible, devolver un mensaje claro en vez de romper el arranque
        return HttpResponse(
            "ReportLab no está instalado en este entorno. Para generar PDFs instala el paquete 'reportlab'.",
            status=501,
        )

    # Detectar si la factura tiene monedas mixtas
    moneda_codigos = set(d.moneda.codigo for d in detalles if getattr(d, 'moneda', None))
    moneda_simbolos = {d.moneda.codigo: (d.moneda.simbolo or '') for d in detalles if getattr(d, 'moneda', None)}
    if len(moneda_codigos) == 1:
        moneda_unica = moneda_codigos.pop()
        moneda_simbolo = moneda_simbolos.get(moneda_unica, moneda_unica)
        mixed = False
    elif len(moneda_codigos) > 1:
        moneda_unica = None
        moneda_simbolo = ''
        mixed = True
    else:
        moneda_unica = getattr(settings, 'DEFAULT_CURRENCY', 'USD')
        moneda_simbolo = moneda_unica
        mixed = False

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Factura_{factura.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14, spaceAfter=12, alignment=1)
    company_style = ParagraphStyle('Company', parent=styles['Normal'], fontSize=12, spaceAfter=6, alignment=1, textColor=colors.black)
    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=9, spaceAfter=3, textColor=colors.black)
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7, spaceAfter=3, textColor=colors.black, alignment=0)
    fecha_style = ParagraphStyle('Fecha', parent=footer_style, alignment=0)

    fecha_local = localtime(factura.fecha)

    # Logo de la empresa
    try:
        logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo-empresa.png")
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=80, height=80)
            logo.hAlign = 'CENTER'
            elements.append(logo)
        elements.append(Paragraph("GONZALEZ S.A", company_style))
    except Exception as e:
        print(f"Error cargando logo: {e}")
        elements.append(Paragraph("GONZALEZ S.A", company_style))

    # Información empresa
    elements.append(Paragraph("Nit: 000000000-0", info_style))
    elements.append(Paragraph("Dolores Carazo", info_style))
    elements.append(Paragraph("Tel: 85727222", info_style))

    # Título factura
    elements.append(Paragraph("FACTURA ELECTRONICA DE VENTA", title_style))

    # Información de la factura
    info_data = [
        [Paragraph(f"<b>No.</b>{factura.id}", info_style),
         Paragraph(f"<b>Cliente:</b> {factura.cliente.nombre if factura.cliente else 'Consumidor Final'}", info_style)],
        [Paragraph(f"<b>Fecha:</b> {fecha_local.strftime('%Y-%m-%d')}", info_style),
         Paragraph(f"<b>Nit:</b> {factura.cliente.nit if factura.cliente and factura.cliente.nit else 'CF'}", info_style)],
        [Paragraph(f"<b>Hora:</b> {fecha_local.strftime('%I:%M:%S %p')}", info_style),
         Paragraph(f"<b>Dirección:</b> {factura.cliente.direccion if factura.cliente and factura.cliente.direccion else '-'}", info_style)],
        [Paragraph("", info_style),
         Paragraph(f"<b>Tel:</b> {factura.cliente.telefono if factura.cliente and factura.cliente.telefono else '-'}", info_style)],
        [Paragraph("", info_style),
         Paragraph(f"<b>Ciudad:</b> {factura.cliente.ciudad if factura.cliente and factura.cliente.ciudad else '-'}", info_style)],
    ]
    info_table = Table(info_data, colWidths=[doc.width/2.0]*2)
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(info_table)

    # Forma de pago y vendedor
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(f"<b>Forma de Pago:</b> {factura.get_tipo_venta_display()}", info_style))
    elements.append(Paragraph(f"<b>Vendedor:</b> {factura.usuario.get_full_name() or factura.usuario.username}", info_style))
    elements.append(Spacer(1, 0.3*cm))

    # Tabla productos
    product_data = [['Cant', 'Detalle', 'Iva', 'P. Unitario', 'Total']]
    for detalle in detalles:
        # usar el símbolo del propio detalle si existe, si no usar el código
        simbolo_det = ''
        try:
            simbolo_det = detalle.moneda.simbolo if detalle.moneda and detalle.moneda.simbolo else detalle.moneda.codigo if detalle.moneda else ''
        except Exception:
            simbolo_det = ''

        product_data.append([
            str(detalle.cantidad),
            detalle.producto.nombre,
            '19' if detalle.iva else '0',
            f"{simbolo_det}{detalle.precio_unitario:.2f}",
            f"{simbolo_det}{detalle.total_con_iva:.2f}"
        ])
    product_table = Table(product_data,
                         colWidths=[doc.width*0.05, doc.width*0.55, doc.width*0.10, doc.width*0.15, doc.width*0.15],
                         repeatRows=1)
    product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(product_table)
    elements.append(Spacer(1, 0.3*cm))

    # Totales
    total_data = []
    if not mixed and moneda_unica:
        pref = moneda_simbolo or moneda_unica
        total_data = [
            ['Subtotal:', f"{pref}{factura.subtotal:.2f}"],
            ['Iva:', f"{pref}{factura.iva_total:.2f}"],
            ['Total:', f"{pref}{factura.total:.2f}"]
        ]
        if factura.tipo_venta == 'contado':
            total_data.extend([
                ['Recibido:', f"{pref}{factura.monto_recibido:.2f}"],
                ['Cambio:', f"{pref}{factura.vuelto:.2f}"]
            ])
    else:
        # Monedas mixtas: mostrar totales sin símbolo y agregar nota
        total_data = [
            ['Subtotal:', f"{factura.subtotal:.2f}"],
            ['Iva:', f"{factura.iva_total:.2f}"],
            ['Total:', f"{factura.total:.2f}"]
        ]
        if factura.tipo_venta == 'contado':
            total_data.extend([
                ['Recibido:', f"{factura.monto_recibido:.2f}"],
                ['Cambio:', f"{factura.vuelto:.2f}"]
            ])
    total_table = Table(total_data, colWidths=[doc.width/3.0, doc.width/3.0])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),
        ('LINEABOVE', (0, 2), (1, 2), 1, colors.black),
        ('FONTSIZE', (0, 2), (1, 2), 11),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 0.3*cm))

    # Detalles de impuestos
    elements.append(Paragraph("<b>DETALLES DE IMPUESTOS</b>", info_style))
    tax_data = [['% IVA', 'BASE', 'VALOR IVA']]
    # Para la tabla de impuestos usamos el prefijo si no es mixto
    if not mixed and moneda_simbolo:
        tax_data.append(['19', f"{moneda_simbolo}{factura.subtotal:.2f}", f"{moneda_simbolo}{factura.iva_total:.2f}"])
    else:
        tax_data.append(['19', f"{factura.subtotal:.2f}", f"{factura.iva_total:.2f}"])
    tax_table = Table(tax_data, colWidths=[doc.width/4.0]*3)
    tax_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (-1, 1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(tax_table)

    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(f"<b>Cantidad items:</b> {len(detalles)}", info_style))

    # QR centrado con info completa
    # QR: incluir moneda o nota de mezcla
    total_display = f"{moneda_simbolo}{factura.total:.2f}" if (not mixed and moneda_simbolo) else f"{factura.total:.2f}"
    moneda_note = moneda_unica if (not mixed and moneda_unica) else ('MULTI' if mixed else '')
    qr_text = f"""
Factura No: {factura.id}
Cliente: {factura.cliente.nombre if factura.cliente else 'Consumidor Final'}
NIT: {factura.cliente.nit if factura.cliente and factura.cliente.nit else 'CF'}
Total: {total_display} {moneda_note}
Fecha: {fecha_local.strftime('%Y-%m-%d %H:%M:%S')}
Vendedor: {factura.usuario.get_full_name() or factura.usuario.username}
"""
    qr_code = qr.QrCodeWidget(qr_text)
    bounds = qr_code.getBounds()
    size = 80
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size/w, 0, 0, size/h, 0, 0])
    d.add(qr_code)

    qr_table = Table([[d]], colWidths=[doc.width])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(qr_table)

    # Pie de página y fechas
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph("Impreso por: GONZALEZ S.A — RUC: 1234567890000", footer_style))
    elements.append(Paragraph("Autorización de la DGI: No. 18900234 del 2024-01-01", footer_style))
    elements.append(Paragraph("Esta factura fue generada electrónicamente y tiene validez legal conforme normativa DGI Nicaragua.", footer_style))

    doc.build(elements)
    return response

# Inicialización de Stripe se hace de forma perezosa dentro de las vistas
def _init_stripe():
    key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if key:
        stripe.api_key = key
    return key

def crear_pago_tarjeta(request, factura_id):
    # Esta vista acepta dos modos:
    # - POST con JSON: { monto: <number>, currency: 'USD' }
    # - GET/URL con factura_id para compatibilidad (no recomendado)
    factura = None
    monto = None
    currency = None

    try:
        org = getattr(request, 'organizacion', None)
        if request.method == 'POST' and request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8') or '{}')
            monto = Decimal(str(body.get('monto', '0')))
            currency = (body.get('currency') or body.get('moneda') or '').lower()
            # si se envia factura_id en body
            factura_id_body = body.get('factura_id')
            if factura_id_body:
                if org is not None:
                    factura = Factura.objects.filter(organizacion=org, id=int(factura_id_body)).first()
                else:
                    factura = Factura.objects.filter(id=int(factura_id_body)).first()

        # Si no vino por POST JSON y se proporcionó factura_id por URL
        if not monto and factura_id:
            if org is not None:
                factura = Factura.objects.filter(organizacion=org, id=factura_id).first()
            else:
                factura = Factura.objects.filter(id=factura_id).first()
            if factura:
                monto = factura.total
                currency = 'usd'  # fallback

        # Validaciones
        if monto is None:
            return JsonResponse({'error': 'Monto no especificado'}, status=400)

        # Fallback a moneda USD si no se indicó
        if not currency:
            # intentar inferir del factura o de la configuración de tienda
            if factura and factura.detalles.exists():
                first_det = factura.detalles.first()
                if first_det and first_det.moneda:
                    currency = first_det.moneda.codigo.lower()
            if not currency:
                currency = getattr(settings, 'DEFAULT_CURRENCY', 'usd')

        # Inicializar Stripe con la clave (si está configurada)
        _init_stripe()

        # Crear un Payment Intent en Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(monto * 100),  # Stripe usa centavos
            currency=currency,
            metadata={
                'factura_id': factura.id if factura else '',
                'cliente': factura.cliente.nombre if factura and factura.cliente else 'Consumidor Final'
            }
        )

        return JsonResponse({
            'clientSecret': intent.client_secret,
            'factura_id': factura.id if factura else None,
            'monto': float(monto)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def webhook_stripe(request):
    # Esta vista maneja las notificaciones de Stripe
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        _init_stripe()
        event = stripe.Webhook.construct_event(
            payload, sig_header, getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Manejar el evento de pago exitoso
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        factura_id = payment_intent.metadata.get('factura_id')

        if factura_id:
            try:
                # Webhooks are external and may not include org context; attempt to find by id.
                factura = Factura.objects.filter(id=factura_id).first()
                if factura:
                    factura.estado_pago = 'completado'
                    factura.id_transaccion = payment_intent.id
                    factura.pagada = True
                    factura.save()
            except Exception:
                pass
    
    return HttpResponse(status=200)