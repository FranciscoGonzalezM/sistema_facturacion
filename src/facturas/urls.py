#facturas/urls.py
from django.urls import path
from . import views

app_name = 'facturas'
urlpatterns = [
    path('nueva/', views.facturar, name='facturar'),
    path('', views.factura_list, name='factura_list'),
    path('<int:pk>/', views.factura_detalle, name='factura_detalle'),
    path('<int:pk>/pdf/', views.factura_pdf, name='factura_pdf'),
    path('crear-pago-tarjeta/<int:factura_id>/', views.crear_pago_tarjeta, name='crear_pago_tarjeta'),
    path('crear-pago-tarjeta/', views.crear_pago_tarjeta, name='crear_pago_tarjeta_sin_id'),
    path('webhook-stripe/', views.webhook_stripe, name='webhook_stripe'),
]

# Install Stripe Python library
# Run the following command in your terminal:
# pip install stripe