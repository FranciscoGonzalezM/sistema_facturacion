#!/usr/bin/env bash
# Script de inicio para Render.com

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario si no existe
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Iniciar la aplicación
exec gunicorn tienda.wsgi:application
