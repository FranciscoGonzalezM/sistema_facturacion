from django.urls import path
from . import views


urlpatterns = [
    path('', views.producto_list, name='producto_list'),
    path('crear/', views.producto_create, name='producto_create'),
    path('editar/<int:pk>/', views.producto_edit, name='producto_edit'),
    path('<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    # Agrega eliminar si tienes
    
    # Nuevas URLs para monedas (usando las vistas de views.py)
    path('monedas/', views.lista_monedas, name='lista_monedas'),
    path('monedas/crear/', views.crear_moneda, name='crear_moneda'),
    path('monedas/editar/<int:pk>/', views.editar_moneda, name='editar_moneda'),
    path('configuracion-tienda/', views.configurar_tienda, name='configurar_tienda'),
]