from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.producto_list, name='producto_list'),
    path('crear/', views.producto_create, name='producto_create'),
    path('editar/<int:pk>/', views.producto_edit, name='producto_edit'),
    path('<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    path('<int:pk>/detalle/', views.producto_detalle, name='producto_detalle'),
    
    # API
    path('api/precio/<int:pk>/', views.calcular_precio, name='calcular_precio'),
    # Monedas y configuración
    path('monedas/', views.lista_monedas, name='lista_monedas'),
    path('monedas/crear/', views.crear_moneda, name='crear_moneda'),
    path('monedas/editar/<int:pk>/', views.editar_moneda, name='editar_moneda'),
    path('configurar/', views.configurar_tienda, name='configurar_tienda'),
]
