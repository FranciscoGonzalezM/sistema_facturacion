from django.urls import path
from . import views

app_name = 'categorias'

urlpatterns = [
    path('', views.categoria_list, name='categoria_list'),
    path('crear/', views.categoria_create, name='categoria_create'),
    path('editar/<int:pk>/', views.categoria_edit, name='categoria_edit'),
    path('<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),
]