"""
Django settings for Consultorio Dental - Sistema de Gestión de Citas.
Configuración segura basada en variables de entorno (python-decouple).
"""

import os
import platform
from pathlib import Path
from decouple import config, Csv

# =============================================================================
# RUTAS BASE
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SEGURIDAD - LEER DESDE VARIABLES DE ENTORNO
# =============================================================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1',
    cast=Csv()
)

# =============================================================================
# APLICACIONES INSTALADAS
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages', # <--- AGREGA ESTA LÍNEA

    'apps.usuarios',
    'apps.agenda',
    'apps.citas',
    'apps.fichas',
]

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# =============================================================================
# PLANTILLAS
# =============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# BASE DE DATOS
# =============================================================================
DB_HOSTNAME = config('DB_HOSTNAME', default='')

if DB_HOSTNAME:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='dental_db'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': DB_HOSTNAME,
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {'sslmode': config('DB_SSLMODE', default='require')},
            'CONN_MAX_AGE': 60,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# SESIONES, USUARIOS, INTERNACIONALIZACIÓN (SIN CAMBIOS)
# =============================================================================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
AUTH_USER_MODEL = 'usuarios.Usuario'
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# =============================================================================
# ARCHIVOS ESTÁTICOS
# =============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# ARCHIVOS DE MEDIA (AZURE STORAGE)
# =============================================================================
MEDIA_URL = '/media/'

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "azure_container": "media",
            "connection_string": config('AZURE_CONNECTION_STRING'),
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# =============================================================================
# RESTO DE CONFIGURACIONES (LOGIN, LOGGING, ETC.)
# =============================================================================
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}

APPEND_SLASH = False
