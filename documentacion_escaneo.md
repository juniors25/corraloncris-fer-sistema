# Documentación de Escaneo de Códigos

## Opciones Implementadas

### 1. Escaneo Web con Cámara (Recomendado para inicio)
**URL**: `http://127.0.0.1:8000/productos/escaneo-movil/`

Esta opción permite usar la cámara del dispositivo móvil directamente desde el navegador web.

#### Características:
- ✅ No requiere instalación de app
- ✅ Funciona en cualquier navegador moderno
- ✅ Soporta códigos de barras y QR
- ✅ Entrada manual como alternativa
- ✅ Actualización de stock en tiempo real
- ✅ Interfaz optimizada para móviles

#### Cómo usar:
1. Acceder a: `http://127.0.0.1:8000/productos/escaneo-movil/`
2. Seleccionar tipo de código (barras/QR)
3. Click en "Activar Cámara"
4. Aceptar permisos de cámara
5. Centrar el código en el recuadro verde
6. El sistema detectará automáticamente el código
7. Se mostrará la información del producto
8. Podrás actualizar el stock (+ entrada, - salida)

#### Requisitos:
- Navegador moderno con soporte de cámara
- Permisos de cámara activados
- Conexión a internet (para cargar la librería ZXing)

---

### 2. API REST para App Móvil Dedicada
Esta opción es para cuando desarrolles una app móvil nativa (React Native, Flutter, etc.).

#### Endpoints Disponibles:

##### GET `/api/v1/productos/`
Obtener lista de todos los productos activos.

**Respuesta:**
```json
{
  "success": true,
  "productos": [
    {
      "id": 1,
      "nombre": "Martillo Carpintero 500g",
      "codigo_barras": "779123456001",
      "codigo_qr": null,
      "precio_venta": "4500.00",
      "precio_costo": "2500.00",
      "stock_actual": 50,
      "categoria": "Herramientas Manuales"
    }
  ],
  "total": 25
}
```

##### GET `/api/v1/producto/codigo/?codigo=CODIGO&tipo=barras`
Buscar producto por código de barras o QR.

**Parámetros:**
- `codigo`: Código a buscar
- `tipo`: 'barras' o 'qr' (default: 'barras')

**Respuesta:**
```json
{
  "success": true,
  "producto": {
    "id": 1,
    "nombre": "Martillo Carpintero 500g",
    "codigo_barras": "779123456001",
    "precio_venta": "4500.00",
    "stock_actual": 50
  }
}
```

##### POST `/api/v1/stock/actualizar/`
Actualizar stock de un producto.

**Body:**
```json
{
  "producto_id": 1,
  "cantidad": 10,
  "tipo": "entrada",
  "motivo": "Escaneo móvil",
  "api_key": "tu_api_key_secreta"
}
```

**Respuesta:**
```json
{
  "success": true,
  "producto_id": 1,
  "nuevo_stock": 60,
  "mensaje": "Stock actualizado correctamente. Nuevo stock: 60"
}
```

##### GET `/api/v1/stock/movimientos/?producto_id=1`
Obtener movimientos de stock de un producto.

##### GET `/api/v1/estadisticas/`
Obtener estadísticas generales del inventario.

#### Autenticación:
Los endpoints requieren un `api_key` en el body de las peticiones POST.
Configura tu API key en el código: `api_views.py` línea 85.

---

## Flujo de Trabajo Recomendado

### Para Operaciones Rápidas (Web):
1. Abre el navegador en tu móvil
2. Accede a la URL del sistema
3. Ve a "Escaneo Móvil"
4. Escanea el código del producto
5. Actualiza el stock según corresponda

### Para Integración Profesional (App):
1. Desarrolla app móvil (React Native/Flutter)
2. Integra con la API REST
3. Implementa escaneo con cámara nativa
4. Sincroniza datos con el servidor

---

## Configuración de Códigos

### Códigos de Barras:
- Formato: EAN-13, EAN-8, UPC-A, UPC-E
- Longitud: 8, 12, o 13 dígitos
- Ejemplo: `779123456001`

### Códigos QR:
- Formato: QR Code estándar
- Contenido: Código de producto o URL
- Ejemplo: `PROD-001` o URL del producto

---

## Solución de Problemas

### La cámara no funciona:
1. Verifica permisos del navegador
2. Asegúrate de usar HTTPS en producción
3. Prueba con otro navegador
4. Usa la entrada manual como alternativa

### Código no se detecta:
1. Asegúrate de buena iluminación
2. Mantén el código estable
3. Centra el código en el recuadro
4. Prueba con entrada manual

### Error de stock:
1. Verifica stock disponible antes de salida
2. Usa tipo 'entrada' para agregar stock
3. Revisa movimientos de stock

---

## Ejemplo de Integración con App Móvil

### React Native (con react-native-camera):
```javascript
import { RNCamera } from 'react-native-camera';

const handleBarCodeRead = ({ data }) => {
  fetch('http://tu-servidor.com/api/v1/producto/codigo/', {
    method: 'GET',
    headers: {
      'codigo': data,
      'tipo': 'barras'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Mostrar información del producto
      setProducto(data.producto);
    }
  });
};
```

### Flutter (con mobile_scanner):
```dart
import 'package:mobile_scanner/mobile_scanner.dart';

void onDetect(BarcodeCapture capture) {
  final barcode = capture.barcodes.first;
  final codigo = barcode.rawValue;
  
  // Llamar a la API
  // ...
}
```

---

## Próximos Pasos

1. **Prueba la versión web** actual
2. **Define necesidades específicas** de tu operación
3. **Decide entre web vs app** dedicada
4. **Configura API keys** para producción
5. **Implementa autenticación** adicional si es necesario