from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    # Proveedores
    path('', views.ProveedorListView.as_view(), name='lista'),
    path('buscar/', views.buscar_proveedores, name='buscar'),
    path('nuevo/', views.ProveedorCreateView.as_view(), name='crear'),
    path('<int:pk>/', views.ProveedorDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.ProveedorUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.ProveedorDeleteView.as_view(), name='eliminar'),
    
    # Contactos
    path('<int:proveedor_id>/contacto/nuevo/', views.ContactoCreateView.as_view(), name='contacto_crear'),
    
    # Pedidos
    path('<int:proveedor_id>/pedido/nuevo/', views.PedidoCreateView.as_view(), name='pedido_crear'),
    path('pedido/<int:pk>/', views.PedidoDetailView.as_view(), name='detalle_pedido'),
]