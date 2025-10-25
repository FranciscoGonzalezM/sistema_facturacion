from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from categorias.models import Categoria
from categorias.forms import CategoriaForm

def categoria_list(request):
    categorias = Categoria.objects.all()
    return render(request, 'core/categoria_list.html', {'categorias': categorias})

@staff_member_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoria_list')
    else:
        form = CategoriaForm()
    return render(request, 'core/categoria_form.html', {'form': form})

def categoria_edit(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        return redirect('categoria_list')
    return render(request, 'core/categoria_form.html', {'form': form})

@staff_member_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.delete()
        return redirect('categoria_list')
    return render(request, 'core/categoria_confirm_delete.html', {'categoria': categoria})
