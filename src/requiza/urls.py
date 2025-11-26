from django.urls import path
from . import views

app_name = 'requiza'

urlpatterns = [
    path('', views.listar_requizas, name='requiza_list'),
    path('nueva/', views.nueva_requiza, name='nueva_requiza'),
]