from django.urls import path
from . import views

app_name = 'articulos'

urlpatterns = [
    path('', views.articulo_list, name='articulo_list'),
    path('crear/', views.articulo_create, name='articulo_create'),
    path('editar/<int:pk>/', views.articulo_edit, name='articulo_edit'),
    path('<int:pk>/eliminar/', views.articulo_delete, name='articulo_delete'),
    
    # URLs para monedas
    path('monedas/', views.lista_monedas, name='lista_monedas'),
    path('monedas/crear/', views.crear_moneda, name='crear_moneda'),
    path('monedas/editar/<int:pk>/', views.editar_moneda, name='editar_moneda'),
    path('configuracion-tienda/', views.configurar_tienda, name='configurar_tienda'),
    
    # API para búsqueda
    path('buscar/', views.buscar_articulo_por_codigo, name='buscar_articulo'),
]


