from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('login')

@login_required
def dashboard(request):
    from productos.models import Producto
    from ventas.models import Venta, PedidoOnline
    from clientes.models import Cliente
    from django.db.models import F, Sum
    
    context = {
        'total_productos': Producto.objects.count(),
        'stock_bajo': Producto.objects.filter(stock_actual__lte=F('stock_minimo')).count(),
        'ventas_hoy': Venta.objects.filter(created_at__date=timezone.now().date()).count(),
        'pedidos_pendientes': PedidoOnline.objects.filter(estado='recibido').count(),
        'total_clientes': Cliente.objects.count(),
        'clientes_morosos': Cliente.objects.filter(estado_credito='moroso').count(),
        'clientes_bloqueados': Cliente.objects.filter(estado_credito='bloqueado').count(),
        'deuda_total': Cliente.objects.aggregate(total=Sum('saldo_deudor'))['total'] or 0,
    }
    return render(request, 'usuarios/dashboard.html', context)
