from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Producto, MovimientoStock
from django.contrib import messages

@login_required
def escaneo_movil(request):
    """Vista optimizada para escaneo con cámara móvil"""
    return render(request, 'productos/escaneo_movil.html')

@login_required
def procesar_escaneo_movil(request):
    """Procesar código escaneado desde móvil"""
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        tipo_codigo = request.POST.get('tipo_codigo', 'barras')
        
        try:
            if tipo_codigo == 'barras':
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
                }
            })
        except Producto.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Producto no encontrado'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def actualizar_stock_movil(request):
    """Actualizar stock desde móvil"""
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 0))
        tipo_movimiento = request.POST.get('tipo', 'entrada')  # 'entrada' o 'salida'
        motivo = request.POST.get('motivo', 'Escaneo móvil')
        
        try:
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
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})