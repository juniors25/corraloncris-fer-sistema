from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Producto, Categoria, MovimientoStock
from django.http import JsonResponse
import json

def catalogo(request):
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.all()
    
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('busqueda')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'user': request.user,
    }
    return render(request, 'productos/catalogo.html', context)

@login_required
def escanear_producto(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        tipo_codigo = request.POST.get('tipo_codigo', 'barras')  # 'barras' o 'qr'
        
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
                    'precio': str(producto.precio_venta),
                    'stock': producto.stock_actual,
                }
            })
        except Producto.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Producto no encontrado'
            })
    
    return render(request, 'productos/escanear.html')

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    context = {
        'producto': producto,
        'user': request.user,
    }
    return render(request, 'productos/detalle.html', context)
