"""
Configuración para instalación local del cliente
Base de datos SQLite local + sincronización opcional con nube
"""

from .settings import *

# Base de datos local (siempre local, funciona sin internet)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'ferreteria_local.db',
    }
}

# Modo de operación local/local-híbrido
MODO_OPERACION = 'local_hibrido'  # 'local' (solo local) o 'local_hibrido' (local + sincronización)

# Configuración de sincronización (opcional)
SINCRONIZACION_HABILITADA = True
SINCRONIZACION_URL = 'https://tu-servidor-nube.com/api/sync/'
SINCRONIZACION_INTERVALO = 300  # cada 5 minutos

# Configuración de impresión local
IMPRESION_HABILITADA = True
IMPRESORA_POR_DEFECTO = 'Canon'  # nombre de impresora predeterminada

# Configuración de archivos locales
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Local custom settings
STATIC_ROOT = BASE_DIR / 'staticfiles_local'