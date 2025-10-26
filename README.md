# Sistema de Facturación

Sistema de facturación desarrollado en Django para gestión de productos, clientes, facturas y más.

## Estructura del Proyecto

```
src/
├── tienda/                 # Configuración principal de Django
│   ├── settings.py        # Configuración del proyecto
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuración WSGI para producción
├── core/                  # Aplicación principal
├── categorias/            # Gestión de categorías
├── productos/           # Gestión de productos
├── clientes/             # Gestión de clientes
├── facturas/             # Gestión de facturas
├── proveedores/          # Gestión de proveedores
├── dashboard/            # Panel de control
├── static/              # Archivos estáticos
├── templates/           # Plantillas HTML
├── requirements.txt     # Dependencias de Python
├── runtime.txt         # Versión de Python
└── build.sh            # Script de construcción para Render
```

## Despliegue en Render.com

### Configuración Requerida

1. **Variables de Entorno en Render:**
   - `SECRET_KEY`: Clave secreta de Django (se genera automáticamente)
   - `DEBUG`: False (para producción)
   - `DATABASE_URL`: URL de la base de datos PostgreSQL (se configura automáticamente)

2. **Configuración del Servicio:**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn tienda.wsgi:application`
   - **Python Version**: 3.11.0

### Pasos para Desplegar

1. **Subir el código a GitHub:**
   ```bash
   git add .
   git commit -m "Preparado para despliegue en Render"
   git push origin main
   ```

2. **En Render.com:**
   - Crear un nuevo Web Service
   - Conectar con tu repositorio de GitHub
   - Usar la configuración del archivo `render.yaml`
   - O configurar manualmente:
     - **Root Directory**: `src`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn tienda.wsgi:application`

3. **Base de Datos:**
   - Crear una base de datos PostgreSQL en Render
   - La variable `DATABASE_URL` se configurará automáticamente

### Características del Sistema

- ✅ Gestión de productos y categorías
- ✅ Gestión de clientes y proveedores
- ✅ Sistema de facturación completo
- ✅ Panel de control (dashboard)
- ✅ Generación de PDFs
- ✅ Integración con Stripe (configurable)
- ✅ Archivos estáticos optimizados con WhiteNoise
- ✅ Configuración de seguridad para producción

### Acceso al Sistema

Una vez desplegado, podrás acceder al sistema en la URL proporcionada por Render. El usuario administrador se crea automáticamente:
- **Usuario**: admin
- **Contraseña**: admin123

**¡IMPORTANTE!** Cambia la contraseña del administrador después del primer acceso.

### Desarrollo Local

Para ejecutar localmente:

```bash
cd src
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Notas Importantes

- El sistema está configurado para usar PostgreSQL en producción
- Los archivos estáticos se sirven con WhiteNoise
- La configuración de seguridad está optimizada para HTTPS
- Se incluye un script de build que maneja migraciones y recolección de archivos estáticos
