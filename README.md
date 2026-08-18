# Sistema de Gestión para Ferretería Corralón

Sistema completo de gestión para ferretería/corralón con funcionalidades de inventario, ventas en línea, gestión de clientes y proveedores.

## Características Implementadas

### ✅ Funcionalidades Completas
- **Sistema de Autenticación**: Login de administrador con roles (admin/empleado)
- **Gestión de Stock**: Control de inventario con códigos de barras/QR
- **Catálogo Web**: Catálogo público vinculado directamente al stock
- **Ventas Locales**: Sistema de ventas en el local con carrito
- **Ventas Online**: Pedidos en línea con gestión de estados
- **Gestión de Clientes**: CRUD completo de clientes
- **Gestión de Proveedores**: CRUD completo de proveedores
- **Dashboard**: Panel de control con estadísticas en tiempo real
- **Sistema de Reportes**: Informes de ventas, productos, clientes y pedidos online
- **Integración ARCA**: Módulo preparado para facturación electrónica (requiere configuración de API keys)
- **WhatsApp API**: Módulo preparado para notificaciones automáticas (requiere configuración de WhatsApp Business API)

### 🔲 Funcionalidades Pendientes de Implementación
- **Integración ARCA**: Módulo preparado para facturación electrónica (requiere configuración de API keys)
- **WhatsApp API**: Módulo preparado para notificaciones automáticas (requiere configuración de WhatsApp Business API)
- **App Móvil**: Aplicación dedicada para escaneo de códigos
- **App Móvil**: Aplicación dedicada para escaneo de códigos

## Stack Tecnológico

- **Backend**: Python 3.12 + Django 6.1
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML + CSS + JavaScript vanilla
- **Escaneo**: App móvil separada (pendiente)

## Instalación y Configuración

### Requisitos Previos
- Python 3.12 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Clonar el repositorio** (o navegar al directorio del proyecto)
   ```bash
   cd ferreteria_corralon
   ```

2. **Instalar dependencias**
   ```bash
   pip install django psycopg2-binary pillow
   ```

3. **Ejecutar migraciones**
   ```bash
   python manage.py migrate
   ```

4. **Crear superusuario** (ya creado por defecto)
   - Usuario: `admin`
   - Contraseña: `admin123`

## Uso del Sistema

### Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: `http://127.0.0.1:8000`

### Acceso al Sistema

1. **Login**: `http://127.0.0.1:8000/login/`
   - Usuario: `admin`
   - Contraseña: `admin123`

2. **Dashboard**: `http://127.0.0.1:8000/dashboard/`

3. **Panel de Administración**: `http://127.0.0.1:8000/admin/`

### Funcionalidades Principales

#### Gestión de Productos
- **Catálogo**: `http://127.0.0.1:8000/productos/`
- **Escaneo**: `http://127.0.0.1:8000/productos/escanear/`
- **Admin**: Panel Django para gestión completa

#### Ventas
- **Nueva Venta Local**: `http://127.0.0.1:8000/ventas/nueva/`
- **Pedido Online**: `http://127.0.0.1:8000/ventas/online/`
- **Gestión de Pedidos**: `http://127.0.0.1:8000/ventas/pedidos/`

#### Clientes y Proveedores
- **Clientes**: `http://127.0.0.1:8000/clientes/`
- **Proveedores**: `http://127.0.0.1:8000/proveedores/`

## Estructura del Proyecto

```
ferreteria_corralon/
├── config/              # Configuración principal de Django
├── usuarios/            # Sistema de autenticación y usuarios
├── productos/           # Gestión de productos y stock
├── ventas/              # Sistema de ventas y pedidos
├── clientes/            # Gestión de clientes
├── proveedores/         # Gestión de proveedores
├── templates/           # Plantillas HTML
├── static/              # Archivos estáticos
├── media/               # Archivos multimedia (imágenes)
└── manage.py           # Script de gestión de Django
```

## Configuración para Producción

### Base de Datos PostgreSQL

Para cambiar a PostgreSQL en producción:

1. Editar `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ferreteria_db',
        'USER': 'postgres',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

2. Instalar PostgreSQL y crear la base de datos
3. Ejecutar migraciones nuevamente

### Seguridad para Producción

1. Cambiar `SECRET_KEY` en settings.py
2. Configurar `DEBUG = False`
3. Configurar `ALLOWED_HOSTS`
4. Configurar servidor HTTPS
5. Configurar archivos estáticos y media

## Próximos Pasos

1. **Integración ARCA**: Configurar API keys en settings.py para activar facturación electrónica
2. **WhatsApp Business**: Configurar API keys en settings.py para activar notificaciones
3. **App Móvil**: Desarrollar aplicación React Native o Flutter
4. **Informes**: Crear sistema de reportes con gráficos
5. **Despliegue**: Configurar servidor para producción

## Configuración de Integraciones

### ARCA (Facturación Electrónica)

El módulo de integración con ARCA ya está implementado en `integraciones/arca.py`. Para activarlo:

1. Editar `config/settings.py`:
```python
ARCA_API_URL = 'https://api.arca.com.ar/v1'  # URL de producción o demo
ARCA_API_KEY = 'tu_api_key_real'  # API key proporcionada por ARCA
ARCA_CUIT = '20000000000'  # CUIT de la empresa
```

2. Usar la integración en las vistas:
```python
from integraciones import ARCAIntegration, preparar_datos_factura

arca = ARCAIntegration()
datos_factura = preparar_datos_factura(venta, cliente)
resultado = arca.generar_factura(datos_factura)
```

### WhatsApp Business API

El módulo de integración con WhatsApp ya está implementado en `integraciones/whatsapp.py`. Para activarlo:

1. Editar `config/settings.py`:
```python
WHATSAPP_API_URL = 'https://graph.facebook.com/v17.0'
WHATSAPP_PHONE_NUMBER_ID = 'tu_phone_number_id_real'  # ID de WhatsApp Business
WHATSAPP_ACCESS_TOKEN = 'tu_access_token_real'  # Token de acceso
```

2. Usar la integración en las vistas:
```python
from integraciones import WhatsAppIntegration

whatsapp = WhatsAppIntegration()
whatsapp.enviar_mensaje_pedido_confirmado(pedido)
```

## Soporte

Para problemas o consultas, contactar al administrador del sistema.