#!/usr/bin/env bash
# Script de inicio para Render.com

# Ejecutar migraciones
python manage.py migrate

# Iniciar la aplicación
exec gunicorn tienda.wsgi:application --bind 0.0.0.0:$PORT
