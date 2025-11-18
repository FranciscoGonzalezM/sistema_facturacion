from django.shortcuts import render, redirect
from .models import Requiza
from .forms import RequizaForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.contrib import messages

def es_gerente(user):
    return user.is_staff or user.is_superuser  

@login_required
def listar_requizas(request):
    org = getattr(request, 'organizacion', None)
    requizas = Requiza.objects.filter(producto__organizacion=org).order_by('-fecha') if org is not None else Requiza.objects.all().order_by('-fecha')
    return render(request, 'core/requiza_list.html', {'requizas': requizas})


@login_required
@user_passes_test(es_gerente)
def nueva_requiza(request):
    if request.method == 'POST':
        form = RequizaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                requiza = form.save(commit=False)
                requiza.usuario = request.user
                producto = requiza.producto
                if producto.stock >= requiza.cantidad:
                    producto.stock -= requiza.cantidad
                    producto.save()
                    requiza.save()
                    messages.success(request, "Requiza registrada con éxito.")
                    return redirect('requiza_list')  # corregido el nombre
                else:
                    form.add_error('cantidad', 'No hay suficiente stock disponible.')
    else:
        form = RequizaForm()
    return render(request, 'core/requiza_form.html', {'form': form}) 