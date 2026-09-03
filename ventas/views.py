from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from .models import Venta, DetalleVenta, PedidoOnline
from productos.models import Producto, MovimientoStock, ListaPrecios
from clientes.models import Cliente
import uuid
import json

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
                
                # Obtener tipo de venta y lista de precios
                tipo_venta = request.POST.get('tipo_venta', 'local')
                lista_precios_id = request.POST.get('lista_precios')
                
                # Crear venta
                numero = f"V-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                venta = Venta.objects.create(
                    numero=numero,
                    cliente=cliente,
                    tipo_venta=tipo_venta,
                    estado='borrador' if tipo_venta == 'presupuesto' else 'confirmada'
                )
                
                # Procesar items
                items = json.loads(request.POST.get('items'))
                for item in items:
                    producto = Producto.objects.get(id=item['producto_id'])
                    
                    # Obtener precio según lista de precios
                    precio_unitario = producto.precio_venta
                    if lista_precios_id:
                        lista_precios = ListaPrecios.objects.get(id=lista_precios_id)
                        precio_unitario = producto.obtener_precio_lista(lista_precios)
                    
                    detalle = DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=precio_unitario
                    )
                    
                    # Actualizar stock solo si no es presupuesto
                    if tipo_venta != 'presupuesto':
                        producto.actualizar_stock(-item['cantidad'])
                        MovimientoStock.objects.create(
                            producto=producto,
                            tipo='salida',
                            cantidad=item['cantidad'],
                            motivo=f'Venta local #{numero}'
                        )
                
                venta.calcular_total()
                
                # Si es venta a crédito, actualizar estado del cliente
                if cliente and request.POST.get('venta_credito') == 'true' and tipo_venta != 'presupuesto':
                    from clientes.models import FacturaCliente
                    from sync.models import OperacionPendiente
                    
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
                    
                    # Crear factura en el sistema
                    from ventas.models import Factura
                    Factura.objects.create(
                        venta=venta,
                        tipo_comprobante='factura_b',
                        estado_arca='no_generado'
                    )
                    
                    # Agregar operación pendiente para ARCA (si hay internet se procesa, si no queda pendiente)
                    try:
                        from integraciones.arca import procesar_factura_arca
                        # Intentar procesar inmediatamente si hay internet
                        exito, resultado = procesar_factura_arca(venta, usar_demo=False)
                        if not exito:
                            # Si falla, agregar a operaciones pendientes
                            OperacionPendiente.objects.create(
                                tipo_operacion='facturacion_arca',
                                datos={'venta_id': venta.id},
                                estado='pendiente'
                            )
                    except Exception as e:
                        # Si hay error de conexión, agregar a operaciones pendientes
                        OperacionPendiente.objects.create(
                            tipo_operacion='facturacion_arca',
                            datos={'venta_id': venta.id},
                            estado='pendiente'
                        )
                
                return JsonResponse({'success': True, 'venta_id': venta.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - preparar contexto
    listas_precios = ListaPrecios.objects.filter(activa=True)
    return render(request, 'ventas/nueva_venta.html', {'listas_precios': listas_precios})

@login_required
def crear_presupuesto(request):
    """Crear presupuesto que luego se puede convertir en venta"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                cliente_id = request.POST.get('cliente_id')
                cliente = Cliente.objects.get(id=cliente_id) if cliente_id else None
                
                numero = f"P-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                venta = Venta.objects.create(
                    numero=numero,
                    cliente=cliente,
                    tipo_venta='presupuesto',
                    estado='borrador'
                )
                
                items = json.loads(request.POST.get('items'))
                for item in items:
                    producto = Producto.objects.get(id=item['producto_id'])
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=producto.precio_venta
                    )
                
                venta.calcular_total()
                return JsonResponse({'success': True, 'venta_id': venta.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'ventas/nueva_venta.html', {'modo_presupuesto': True})

@login_required
def lista_presupuestos(request):
    """Lista de presupuestos pendientes"""
    presupuestos = Venta.objects.filter(tipo_venta='presupuesto', estado='borrador')
    return render(request, 'ventas/lista_presupuestos.html', {'presupuestos': presupuestos})

@login_required
def convertir_presupuesto_a_venta(request, presupuesto_id):
    """Convertir presupuesto en venta"""
    presupuesto = get_object_or_404(Venta, id=presupuesto_id)
    
    if presupuesto.tipo_venta == 'presupuesto' and presupuesto.estado == 'borrador':
        # Actualizar stock
        for detalle in presupuesto.items.all():
            producto = detalle.producto
            producto.actualizar_stock(-detalle.cantidad)
            MovimientoStock.objects.create(
                producto=producto,
                tipo='salida',
                cantidad=detalle.cantidad,
                motivo=f'Conversión presupuesto #{presupuesto.numero}'
            )
        
        # Convertir a venta
        presupuesto.tipo_venta = 'local'
        presupuesto.estado = 'confirmada'
        presupuesto.save()
        
        messages.success(request, f'Presupuesto #{presupuesto.numero} convertido a venta exitosamente')
    else:
        messages.error(request, 'Este presupuesto no puede ser convertido')
    
    return redirect('lista_presupuestos')

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

@login_required
def imprimir_factura(request, venta_id):
    """Generar vista de impresión de factura/remito"""
    from django.conf import settings
    
    venta = get_object_or_404(Venta, id=venta_id)
    
    # Configuración del negocio (se puede personalizar)
    nombre_negocio = getattr(settings, 'NOMBRE_NEGOCIO', 'Ferretería Corralón')
    direccion = getattr(settings, 'DIRECCION_NEGOCIO', 'Dirección del negocio')
    telefono = getattr(settings, 'TELEFONO_NEGOCIO', 'Teléfono')
    logo = getattr(settings, 'LOGO_NEGOCIO', 'logo.png')
    
    context = {
        'venta': venta,
        'tipo_comprobante': venta.factura.get_tipo_comprobante_display() if hasattr(venta, 'factura') else 'Remito',
        'numero_comprobante': venta.factura.numero_afip or venta.numero,
        'fecha': venta.created_at.strftime('%d/%m/%Y'),
        'fecha_vencimiento': venta.factura.vencimiento_cae.strftime('%d/%m/%Y') if venta.factura.vencimiento_cae else '-',
        'cliente': venta.cliente,
        'items': venta.items.all(),
        'subtotal': venta.subtotal,
        'iva': venta.total * 0.21,  # 21% IVA
        'total': venta.total,
        'observaciones': venta.observaciones,
        'numero_afip': venta.factura.numero_afip if hasattr(venta, 'factura') else None,
        'nombre_negocio': nombre_negocio,
        'direccion': direccion,
        'telefono': telefono,
        'logo': logo,
    }
    
    return render(request, 'ventas/factura_impresa.html', context)

@login_required
def pos_tactil(request):
    """POS táctil para mostrador"""
    from productos.models import Producto, Categoria, ListaPrecios
    from clientes.models import Cliente
    
    categorias = Categoria.objects.all()
    clientes = Cliente.objects.filter(activo=True)
    listas_precios = ListaPrecios.objects.filter(activa=True)
    
    return render(request, 'ventas/pos_tactil.html', {
        'categorias': categorias,
        'clientes': clientes,
        'listas_precios': listas_precios
    })