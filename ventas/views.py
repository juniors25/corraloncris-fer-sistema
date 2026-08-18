from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Venta, DetalleVenta, PedidoOnline
from productos.models import Producto
from clientes.models import Cliente
import uuid

@login_required
def nueva_venta(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Obtener cliente si existe
                cliente_id = request.POST.get('cliente_id')
                cliente = None
                if cliente_id:
                    cliente = Cliente.objects.get(id=cliente_id)
                
                # Crear venta
                numero = f"V-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                venta = Venta.objects.create(
                    numero=numero,
                    cliente=cliente,
                    tipo_venta='local',
                    estado='confirmada'
                )
                
                # Procesar items
                items = json.loads(request.POST.get('items'))
                for item in items:
                    producto = Producto.objects.get(id=item['producto_id'])
                    detalle = DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=producto.precio_venta
                    )
                    # Actualizar stock
                    producto.actualizar_stock(-item['cantidad'])
                    # Registrar movimiento de stock
                    MovimientoStock.objects.create(
                        producto=producto,
                        tipo='salida',
                        cantidad=item['cantidad'],
                        motivo=f'Venta local #{numero}'
                    )
                
                venta.calcular_total()
                
                # Si es venta a crédito, actualizar estado del cliente
                if cliente and request.POST.get('venta_credito') == 'true':
                    from clientes.models import FacturaCliente
                    # Crear factura de cliente pendiente
                    numero_factura = f"F-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
                    factura_cliente = FacturaCliente.objects.create(
                        cliente=cliente,
                        tipo_comprobante='factura',
                        numero_comprobante=numero_factura,
                        fecha_emision=timezone.now().date(),
                        monto_total=venta.total,
                        estado='pendiente'
                    )
                    # Actualizar saldo deudor del cliente
                    cliente.registrar_factura(numero_factura, venta.total)
                
                return JsonResponse({'success': True, 'venta_id': venta.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'ventas/nueva_venta.html')

def pedido_online(request):
    # Obtener carrito del localStorage si viene del catálogo
    carrito_items = []
    if request.GET.get('carrito') == 'true':
        # Renderizar la página con el carrito del localStorage
        return render(request, 'ventas/pedido_online.html', {'carrito_mode': True})
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Procesar items del carrito
                items = json.loads(request.POST.get('items'))
                
                # Verificar stock antes de procesar
                for item in items:
                    producto = Producto.objects.get(id=item['producto_id'])
                    if producto.stock_actual < item['cantidad']:
                        return JsonResponse({
                            'success': False, 
                            'error': f'Stock insuficiente para {producto.nombre}. Disponible: {producto.stock_actual}, Solicitado: {item["cantidad"]}'
                        })
                
                # Crear cliente temporal si no existe
                cliente, created = Cliente.objects.get_or_create(
                    nombre=request.POST.get('nombre'),
                    telefono=request.POST.get('telefono'),
                    defaults={'email': request.POST.get('email', '')}
                )
                
                # Crear venta
                numero = f"O-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                venta = Venta.objects.create(
                    numero=numero,
                    cliente=cliente,
                    tipo_venta='online',
                    estado='pendiente'
                )
                
                # Procesar items y descontar stock
                for item in items:
                    producto = Producto.objects.get(id=item['producto_id'])
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=producto.precio_venta
                    )
                    # Descontar stock
                    producto.actualizar_stock(-item['cantidad'])
                    # Registrar movimiento de stock
                    MovimientoStock.objects.create(
                        producto=producto,
                        tipo='salida',
                        cantidad=item['cantidad'],
                        motivo=f'Venta online #{numero}'
                    )
                
                venta.calcular_total()
                
                # Crear pedido online
                pedido = PedidoOnline.objects.create(
                    venta=venta,
                    nombre_cliente=request.POST.get('nombre'),
                    telefono=request.POST.get('telefono'),
                    email=request.POST.get('email', ''),
                    direccion_entrega=request.POST.get('direccion', ''),
                    numero_whatsapp=request.POST.get('telefono')
                )
                
                # Enviar notificación de WhatsApp automática
                try:
                    from integraciones import WhatsAppIntegration
                    whatsapp = WhatsAppIntegration()
                    whatsapp.enviar_mensaje_pedido_confirmado(pedido)
                except Exception as e:
                    print(f'Error al enviar WhatsApp: {str(e)}')
                
                return JsonResponse({'success': True, 'pedido_id': pedido.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'ventas/pedido_online.html')

@login_required
def lista_pedidos(request):
    pedidos = PedidoOnline.objects.all().order_by('-created_at')
    return render(request, 'ventas/lista_pedidos.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoOnline, id=pedido_id)
    
    if request.method == 'POST':
        estado_anterior = pedido.estado
        nuevo_estado = request.POST.get('estado')
        
        if nuevo_estado in dict(PedidoOnline.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            
            # Enviar mensaje de WhatsApp si se solicita
            if request.POST.get('enviar_whatsapp') == 'true':
                try:
                    from integraciones import notificar_cambio_estado_pedido
                    notificar_cambio_estado_pedido(pedido, estado_anterior, nuevo_estado)
                    pedido.mensaje_whatsapp_enviado = True
                    pedido.save()
                    messages.success(request, 'Notificación de WhatsApp enviada exitosamente')
                except Exception as e:
                    messages.error(request, f'Error al enviar notificación: {str(e)}')
            else:
                messages.success(request, 'Estado del pedido actualizado')
        
        return redirect('lista_pedidos')
    
    return render(request, 'ventas/detalle_pedido.html', {'pedido': pedido})
