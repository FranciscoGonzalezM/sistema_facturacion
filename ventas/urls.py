from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('punto-venta/', views.punto_venta, name='punto_venta'),
    path('reporte-diario/', views.ventas_dia, name='reporte_dia'),
]