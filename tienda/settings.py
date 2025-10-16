import os
from pathlib import Path
import dj_database_url  # si lo usas (ver nota de dependencias)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'inseguro-en-local')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

def _normalize_host(h: str) -> str:
    if not h:
        return h
    if h.startswith('http://') or h.startswith('https://'):
        h = h.split('://', 1)[1]
    return h.rstrip('/')

render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME') or os.environ.get('RENDER_SERVE_HOST')
env_allowed = os.environ.get('ALLOWED_HOSTS', '')
env_hosts = [h for h in (h.strip() for h in env_allowed.split(',')) if h]

ALLOWED_HOSTS = [
    _normalize_host(h) for h in (
        env_hosts + ['localhost', '127.0.0.1'] + ([render_host] if render_host else [])
    )
]

CSRF_TRUSTED_ORIGINS = [s for s in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if s]

if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# --- Templates (CORREGIDO) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],  # <-- CORRECTO: cierra la lista
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Static files (necesario para Render) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'   # collectstatic lo llenará aquí
STATICFILES_DIRS = [BASE_DIR / 'static']  # si tienes carpeta static en repo

# WhiteNoise (para servir static en producción)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # recomendado justo después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Usar el storage de WhiteNoise para compresión/caching opcional:
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- Database: ejemplo con DATABASE_URL (Postgres en Render) ---
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse('postgresql://sistema_facturacion_8med_user:ymwRKBnI528JeokpAo1eXNszbzRqrYmb@dpg-d3m51vd6ubrc73eh806g-a.oregon-postgres.render.com/sistema_facturacion_8med')
    }
else:
    # sqlite por defecto en local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Resto de settings (INSTALLED_APPS, etc.) se mantienen...


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #"django_extensions",
    'categorias.apps.CategoriasConfig',  # Configuración completa
    'productos.apps.ProductosConfig',
    'clientes.apps.ClientesConfig', 
    'facturas',
    'proveedores',
    'requiza',
    'dashboard.apps.DashboardConfig',
    #'ventas',
    'core',
    'tienda.apps.TiendaConfig',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # << debe estar antes de AuthenticationMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'tienda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'ventas.context_processors.ventas_hoy',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tienda.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'America/Managua'  # zona horaria de Nicaragua

USE_I18N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Ruta a tu carpeta static
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
# =========================
# Configuración de Email
# =========================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # o tu servidor SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gmfrancisco1980@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_aplicacion'
DEFAULT_FROM_EMAIL = 'noreply@tu-dominio.com'
# =========================
# Configuración de sesiones
# =========================

# Usar solo base de datos para sesiones (más estable en desarrollo)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# No guardar sesión en cada request (evita SessionInterrupted)
SESSION_SAVE_EVERY_REQUEST = False

# Expiración de la cookie: 1 día (ajusta si quieres más corto)
SESSION_COOKIE_AGE = 86400  

# Mantener la sesión al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Cookies seguras
SESSION_COOKIE_SECURE = False        # True solo con HTTPS en producción
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'      # Evita problemas con Chrome/Edge

# =========================
# CSRF
# =========================
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost'
]
# If Render provides an external hostname, add it as a trusted origin with https
if render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_normalize_host(render_host)}")

# When running behind a proxy (Render, Cloudflare, etc.) ensure Django
# understands the original request scheme/host. This prevents invalid
# request/host detection (400) when the proxy forwards HTTPS requests.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Allow using forwarded Host header
USE_X_FORWARDED_HOST = True

# Stripe Configuration
STRIPE_PUBLIC_KEY = 'pk_test_tu_llave_publica'  # Reemplaza con tu llave
STRIPE_SECRET_KEY = 'sk_test_tu_llave_secreta'  # Reemplaza con tu llave
STRIPE_WEBHOOK_SECRET = 'whsec_tu_webhook_secret'  # Para webhooks