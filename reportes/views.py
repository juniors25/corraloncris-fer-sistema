from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
from productos.models import Producto, MovimientoStock
from ventas.models import Venta, PedidoOnline
from clientes.models import Cliente
from django.db.models.functions import TruncDay, TruncMonth

@login_required
def dashboard_reportes(request):
    """Vista principal de reportes"""
    return render(request, 'reportes/dashboard.html')

@login_required
def reporte_ventas(request):
    """Reporte de ventas por período"""
    periodo = request.GET.get('periodo', 'hoy')
    
    fecha_inicio = timezone.now().date()
    if periodo == 'hoy':
        fecha_inicio = timezone.now().date()
    elif periodo == 'semana':
        fecha_inicio = timezone.now().date() - timedelta(days=7)
    elif periodo == 'mes':
        fecha_inicio = timezone.now().date() - timedelta(days=30)
    elif periodo == 'anio':
        fecha_inicio = timezone.now().date() - timedelta(days=365)
    
    ventas = Venta.objects.filter(created_at__date__gte=fecha_inicio)
    
    # Estadísticas generales
    total_ventas = ventas.count()
    total_facturado = ventas.aggregate(total=Sum('total'))['total'] or 0
    promedio_venta = total_facturado / total_ventas if total_ventas > 0 else 0
    
    # Ventas por tipo
    ventas_locales = ventas.filter(tipo_venta='local').count()
    ventas_online = ventas.filter(tipo_venta='online').count()
    
    # Ventas por estado
    ventas_completadas = ventas.filter(estado='completada').count()
    ventas_pendientes = ventas.filter(estado='pendiente').count()
    
    context = {
        'periodo': periodo,
        'fecha_inicio': fecha_inicio,
        'total_ventas': total_ventas,
        'total_facturado': total_facturado,
        'promedio_venta': promedio_venta,
        'ventas_locales': ventas_locales,
        'ventas_online': ventas_online,
        'ventas_completadas': ventas_completadas,
        'ventas_pendientes': ventas_pendientes,
        'ventas_recientes': ventas.order_by('-created_at')[:10],
    }
    
    return render(request, 'reportes/ventas.html', context)

@login_required
def reporte_productos(request):
    """Reporte de productos y stock"""
    productos = Producto.objects.all()
    
    # Estadísticas de productos
    total_productos = productos.count()
    productos_activos = productos.filter(activo=True).count()
    productos_inactivos = productos.filter(activo=False).count()
    stock_bajo = productos.filter(stock_actual__lte=F('stock_minimo')).count()
    sin_stock = productos.filter(stock_actual=0).count()
    
    # Valor del inventario
    valor_inventario = sum(p.precio_costo * p.stock_actual for p in productos)
    valor_venta_inventario = sum(p.precio_venta * p.stock_actual for p in productos)
    
    context = {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_inactivos': productos_inactivos,
        'stock_bajo': stock_bajo,
        'sin_stock': sin_stock,
        'valor_inventario': valor_inventario,
        'valor_venta_inventario': valor_venta_inventario,
        'productos_con_stock_bajo': productos.filter(stock_actual__lte=F('stock_minimo'))[:10],
        'productos_sin_stock': productos.filter(stock_actual=0)[:10],
    }
    
    return render(request, 'reportes/productos.html', context)

@login_required
def reporte_clientes(request):
    """Reporte de clientes"""
    clientes = Cliente.objects.all()
    
    # Estadísticas de clientes
    total_clientes = clientes.count()
    clientes_activos = clientes.filter(activo=True).count()
    clientes_inactivos = clientes.filter(activo=False).count()
    
    context = {
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'clientes_inactivos': clientes_inactivos,
        'clientes_recientes': clientes.order_by('-created_at')[:10],
    }
    
    return render(request, 'reportes/clientes.html', context)

@login_required
def reporte_pedidos_online(request):
    """Reporte de pedidos online"""
    pedidos = PedidoOnline.objects.all()
    
    # Estadísticas de pedidos
    total_pedidos = pedidos.count()
    pedidos_recibidos = pedidos.filter(estado='recibido').count()
    pedidos_procesando = pedidos.filter(estado='procesando').count()
    pedidos_listos = pedidos.filter(estado='listo').count()
    pedidos_entregados = pedidos.filter(estado='entregado').count()
    pedidos_cancelados = pedidos.filter(estado='cancelado').count()
    
    # Valor total de pedidos
    valor_pedidos = pedidos.aggregate(total=Sum('venta__total'))['total'] or 0
    
    context = {
        'total_pedidos': total_pedidos,
        'pedidos_recibidos': pedidos_recibidos,
        'pedidos_procesando': pedidos_procesando,
        'pedidos_listos': pedidos_listos,
        'pedidos_entregados': pedidos_entregados,
        'pedidos_cancelados': pedidos_cancelados,
        'valor_pedidos': valor_pedidos,
        'pedidos_recientes': pedidos.order_by('-created_at')[:10],
    }
    
    return render(request, 'reportes/pedidos_online.html', context)