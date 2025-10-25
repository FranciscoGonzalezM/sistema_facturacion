from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_administracion, name='panel_administracion'),
    # Otras URLs específicas del panel
]