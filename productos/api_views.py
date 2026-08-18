"""
API REST para integración con app móvil dedicada
Esta API permite que una app móvil se conecte al sistema para escanear códigos
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Producto, MovimientoStock
import json

@csrf_exempt
@require_http_methods(["GET"])
def api_productos(request):
    """API para obtener lista de productos"""
    productos = Producto.objects.filter(activo=True)
    
    productos_data = []
    for producto in productos:
        productos_data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo_barras': producto.codigo_barras,
            'codigo_qr': producto.codigo_qr,
            'precio_venta': str(producto.precio_venta),
            'precio_costo': str(producto.precio_costo),
            'stock_actual': producto.stock_actual,
            'stock_minimo': producto.stock_minimo,
            'categoria': producto.categoria.nombre if producto.categoria else None,
            'imagen': producto.imagen.url if producto.imagen else None,
        })
    
    return JsonResponse({
        'success': True,
        'productos': productos_data,
        'total': len(productos_data)
    })

@csrf_exempt
@require_http_methods(["GET"])
def api_producto_por_codigo(request):
    """API para buscar producto por código de barras o QR"""
    codigo = request.GET.get('codigo')
    tipo = request.GET.get('tipo', 'barras')  # 'barras' o 'qr'
    
    if not codigo:
        return JsonResponse({
            'success': False,
            'error': 'Código no proporcionado'
        })
    
    try:
        if tipo == 'barras':
            producto = Producto.objects.get(codigo_barras=codigo)
        else:
            producto = Producto.objects.get(codigo_qr=codigo)
        
        return JsonResponse({
            'success': True,
            'producto': {
                'id': producto.id,
                'nombre': producto.nombre,
                'codigo_barras': producto.codigo_barras,
                'codigo_qr': producto.codigo_qr,
                'precio_venta': str(producto.precio_venta),
                'precio_costo': str(producto.precio_costo),
                'stock_actual': producto.stock_actual,
                'stock_minimo': producto.stock_minimo,
                'categoria': producto.categoria.nombre if producto.categoria else None,
                'descripcion': producto.descripcion,
                'imagen': producto.imagen.url if producto.imagen else None,
                'unidad_medida': producto.unidad_medida,
            }
        })
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        })

@csrf_exempt
@require_http_methods(["POST"])
def api_actualizar_stock(request):
    """API para actualizar stock desde app móvil"""
    try:
        data = json.loads(request.body)
        
        producto_id = data.get('producto_id')
        cantidad = int(data.get('cantidad', 0))
        tipo_movimiento = data.get('tipo', 'entrada')  # 'entrada' o 'salida'
        motivo = data.get('motivo', 'App móvil')
        api_key = data.get('api_key')  # Para autenticación básica
        
        # Validar API key (deberías configurar una real)
        if api_key != 'tu_api_key_secreta':
            return JsonResponse({
                'success': False,
                'error': 'No autorizado'
            })
        
        producto = Producto.objects.get(id=producto_id)
        
        # Verificar stock para salidas
        if tipo_movimiento == 'salida' and producto.stock_actual < cantidad:
            return JsonResponse({
                'success': False,
                'error': f'Stock insuficiente. Actual: {producto.stock_actual}, Solicitado: {cantidad}'
            })
        
        # Actualizar stock
        if tipo_movimiento == 'entrada':
            producto.actualizar_stock(cantidad)
        else:
            producto.actualizar_stock(-cantidad)
        
        # Registrar movimiento
        MovimientoStock.objects.create(
            producto=producto,
            tipo=tipo_movimiento,
            cantidad=cantidad,
            motivo=motivo
        )
        
        return JsonResponse({
            'success': True,
            'producto_id': producto.id,
            'nuevo_stock': producto.stock_actual,
            'mensaje': f'Stock actualizado correctamente. Nuevo stock: {producto.stock_actual}'
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@csrf_exempt
@require_http_methods(["GET"])
def api_movimientos_stock(request):
    """API para obtener movimientos de stock de un producto"""
    producto_id = request.GET.get('producto_id')
    
    if not producto_id:
        return JsonResponse({
            'success': False,
            'error': 'ID de producto no proporcionado'
        })
    
    try:
        producto = Producto.objects.get(id=producto_id)
        movimientos = producto.movimientos.all().order_by('-fecha')[:20]
        
        movimientos_data = []
        for mov in movimientos:
            movimientos_data.append({
                'id': mov.id,
                'tipo': mov.tipo,
                'cantidad': mov.cantidad,
                'motivo': mov.motivo,
                'fecha': mov.fecha.isoformat(),
            })
        
        return JsonResponse({
            'success': True,
            'movimientos': movimientos_data,
            'total': len(movimientos_data)
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        })

@csrf_exempt
@require_http_methods(["GET"])
def api_estadisticas(request):
    """API para obtener estadísticas rápidas del inventario"""
    productos = Producto.objects.all()
    
    total_productos = productos.count()
    productos_activos = productos.filter(activo=True).count()
    stock_bajo = productos.filter(stock_actual__lte=10).count()
    sin_stock = productos.filter(stock_actual=0).count()
    
    valor_inventario = sum(p.precio_costo * p.stock_actual for p in productos)
    
    return JsonResponse({
        'success': True,
        'estadisticas': {
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'stock_bajo': stock_bajo,
            'sin_stock': sin_stock,
            'valor_inventario': str(valor_inventario),
        }
    })