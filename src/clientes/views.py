from django.shortcuts import render, get_object_or_404, redirect
from clientes.models import Cliente
from clientes.forms import ClienteForm


def _get_organizacion_from_request(request):
    return getattr(request, 'organizacion', None)

def cliente_list(request):
    org = _get_organizacion_from_request(request)
    clientes = Cliente.objects.filter(organizacion=org) if org is not None else Cliente.objects.all()
    return render(request, 'core/cliente_list.html', {'clientes': clientes})

def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            org = _get_organizacion_from_request(request)
            if org is not None:
                cliente.organizacion = org
            cliente.save()
            return redirect('clientes:cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'core/cliente_form.html', {'form': form})

def cliente_update(request, pk):
    org = _get_organizacion_from_request(request)
    cliente = get_object_or_404(Cliente.objects.filter(organizacion=org) if org is not None else Cliente.objects, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('clientes:cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'core/cliente_form.html', {'form': form})

def cliente_delete(request, pk):
    org = _get_organizacion_from_request(request)
    cliente = get_object_or_404(Cliente.objects.filter(organizacion=org) if org is not None else Cliente.objects, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes:cliente_list')
    return render(request, 'core/cliente_confirm_delete.html', {'cliente': cliente})