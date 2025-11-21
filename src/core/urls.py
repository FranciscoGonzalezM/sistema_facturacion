#URLS APP CORE 

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from facturas.views import facturar 

app_name = 'core'
urlpatterns = [
    path('', views.admin_inicio, name='admin_inicio'),  # Ahora la raíz del namespace apunta al dashboard
    path('inicio/', views.inicio, name='inicio'),
    path('mi-dashboard/', views.panel_administracion, name='tenant_dashboard'),
    path('actividades/', views.actividad_list, name='actividad_list'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
    path('facturar/', facturar, name='facturar'),
]

