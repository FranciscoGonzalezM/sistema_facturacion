#URLS APP CORE 

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('dashboard/', views.admin_inicio, name='admin_inicio'),
    path('actividades/', views.actividad_list, name='actividad_list'),
    path('dashboard-data/', views.dashboard_data, name='dashboard_data'),
]

