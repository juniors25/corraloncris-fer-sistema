from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Cliente
from django.contrib import messages

@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all()
    busqueda = request.GET.get('busqueda')
    
    if busqueda:
        clientes = clientes.filter(nombre__icontains=busqueda)
    
    return render(request, 'clientes/lista.html', {'clientes': clientes})

@login_required
def nuevo_cliente(request):
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.create(
                nombre=request.POST.get('nombre'),
                tipo_documento=request.POST.get('tipo_documento'),
                numero_documento=request.POST.get('numero_documento'),
                email=request.POST.get('email'),
                telefono=request.POST.get('telefono'),
                direccion=request.POST.get('direccion'),
                ciudad=request.POST.get('ciudad'),
                provincia=request.POST.get('provincia'),
                codigo_postal=request.POST.get('codigo_postal'),
                notas=request.POST.get('notas')
            )
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    return render(request, 'clientes/formulario.html')

@login_required
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        cliente.nombre = request.POST.get('nombre')
        cliente.tipo_documento = request.POST.get('tipo_documento')
        cliente.numero_documento = request.POST.get('numero_documento')
        cliente.email = request.POST.get('email')
        cliente.telefono = request.POST.get('telefono')
        cliente.direccion = request.POST.get('direccion')
        cliente.ciudad = request.POST.get('ciudad')
        cliente.provincia = request.POST.get('provincia')
        cliente.codigo_postal = request.POST.get('codigo_postal')
        cliente.notas = request.POST.get('notas')
        cliente.activo = request.POST.get('activo') == 'true'
        cliente.save()
        
        messages.success(request, 'Cliente actualizado exitosamente')
        return redirect('lista_clientes')
    
    return render(request, 'clientes/formulario.html', {'cliente': cliente})
