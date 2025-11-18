from django.urls import path
from . import views

app_name = 'organizaciones'

urlpatterns = [
    path('editar/', views.editar_organizacion, name='editar'),
]
