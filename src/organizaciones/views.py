from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Organizacion, Miembro
from django import forms


class OrganizacionForm(forms.ModelForm):
    class Meta:
        model = Organizacion
        fields = ['nombre', 'logo', 'dominio']


@login_required
def editar_organizacion(request):
    # Determinar la organización del usuario (primera en la que es miembro)
    try:
        miembro = request.user.organizaciones.select_related('organizacion').first()
        organizacion = miembro.organizacion if miembro else None
    except Exception:
        organizacion = None

    if not organizacion:
        messages.error(request, 'No estás asociado a ninguna organización para editar.')
        return redirect('/')

    # Solo propietarios o admins pueden editar
    miembro = Miembro.objects.filter(organizacion=organizacion, user=request.user).first()
    if not miembro or miembro.role not in ('owner', 'admin'):
        messages.error(request, 'No tienes permisos para editar esta organización.')
        return redirect('/')

    if request.method == 'POST':
        form = OrganizacionForm(request.POST, request.FILES, instance=organizacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organización actualizada.')
            return redirect('organizaciones:editar')
    else:
        form = OrganizacionForm(instance=organizacion)

    return render(request, 'organizaciones/editar.html', {'form': form, 'organizacion': organizacion})
