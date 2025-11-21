# URLS PRINCIPAL DE LA APLICACIÓN TIENDA
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.conf import settings
from django.conf.urls.static import static
from core.views import CustomLoginView, custom_logout
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),  # Cambiado a vista personalizada
    
    # URLs para restablecimiento de contraseña
    path('password_reset/', PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Apps
    path('clientes/', include('clientes.urls')),
    path('productos/', include('productos.urls')),
    path('categorias/', include('categorias.urls')),
    path('facturas/', include(('facturas.urls','facturas'), namespace='facturas')),
    path('proveedores/', include(('proveedores.urls', 'proveedores'), namespace='proveedores')),
    path('organizacion/', include('organizaciones.urls')),
    path('requizas/', include('requiza.urls')),
    
    
    path('dashboard/', include(('core.urls', 'core'), namespace='core')),   # ahora Django encuentra 'facturar'
    # Redirección raíz
    path('', lambda request: redirect('login')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)