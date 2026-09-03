# Personalización del Sistema

## 🎨 Personalización Visual

### 1. Agregar Logo del Negocio
- Coloca el archivo del logo en: `static/personalizado/logo_cliente.png`
- Formatos recomendados: PNG, JPG (máximo 2MB)
- Dimensiones recomendadas: 300x150px

### 2. Configurar Colores
Edita `config/settings_cliente.py`:
```python
COLOR_PRINCIPAL = '#e74c3c'  # Color principal
COLOR_SECUNDARIO = '#3498db'  # Color secundario
COLOR_FONDO = '#f8f9fa'  # Color de fondo
```

### 3. Información del Negocio
Edita `config/settings_cliente.py`:
```python
NOMBRE_NEGOCIO = 'CORRALÓN CRIS'
DIRECCION_NEGOCIO = 'Dirección del negocio'
TELEFONO_NEGOCIO = 'Teléfono del negocio'
CUIT_NEGOCIO = '20-00000000-0'
EMAIL_NEGOCIO = 'email@negocio.com'
```

## 🖨️ Impresión de Facturas/Remitos

### Configurar Impresora
Edita `config/settings_cliente.py`:
```python
IMPRESORA_POR_DEFECTO = 'Canon'  # Nombre de la impresora
PAPEL_FORMATO = 'A4'  # Formato de papel
```

### URL de Impresión
- Generar factura: `/ventas/imprimir/<venta_id>/`
- El sistema genera automáticamente formato para impresión

## 🌐 Sistema Híbrido Local/Nube

### Modo de Operación
Edita `config/settings_cliente.py`:
```python
MODO_OPERACION = 'local_hibrido'  # Funciona sin internet, sincroniza cuando hay conexión
```

### Funcionamiento Offline
- ✅ Sistema funciona completamente sin internet
- ✅ Base de datos local (SQLite)
- ✅ Operaciones de facturación ARCA quedan pendientes
- ✅ Mensajes WhatsApp quedan pendientes
- ✅ Al volver a tener internet, se sincronizan automáticamente

### Ver Operaciones Pendientes
- Panel Admin → Operaciones Pendientes
- Puedes procesar manualmente si es necesario
- Sistema reintentará automáticamente cada 5 minutos

## 📦 Instalación Local del Cliente

### Requisitos
- Windows 10/11
- Python 3.12+
- 4GB RAM mínimo
- 10GB espacio en disco

### Pasos de Instalación
1. Copiar carpeta `ferreteria_corralon` al PC del cliente
2. Ejecutar: `python manage.py migrate`
3. Ejecutar: `python manage.py auto_config`
4. Ejecutar: `python manage.py runserver`
5. Acceder a: `http://localhost:8000`

### Credenciales Iniciales
- Usuario: `admin`
- Contraseña: `admin123`

## 🔧 Configuración para Producción

Para uso en producción del cliente:
1. Cambiar contraseña del admin
2. Configurar credenciales reales de ARCA
3. Configurar credenciales reales de WhatsApp
4. Personalizar logo y colores
5. Configurar impresora predeterminada

## 📞 Soporte
Para problemas de instalación o configuración, contactar al desarrollador.