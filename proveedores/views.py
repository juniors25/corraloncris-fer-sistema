from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Proveedor
from django.contrib import messages

@login_required
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    busqueda = request.GET.get('busqueda')
    
    if busqueda:
        proveedores = proveedores.filter(nombre__icontains=busqueda)
    
    return render(request, 'proveedores/lista.html', {'proveedores': proveedores})

@login_required
def nuevo_proveedor(request):
    if request.method == 'POST':
        try:
            proveedor = Proveedor.objects.create(
                nombre=request.POST.get('nombre'),
                cuit=request.POST.get('cuit'),
                email=request.POST.get('email'),
                telefono=request.POST.get('telefono'),
                direccion=request.POST.get('direccion'),
                ciudad=request.POST.get('ciudad'),
                provincia=request.POST.get('provincia'),
                codigo_postal=request.POST.get('codigo_postal'),
                contacto_principal=request.POST.get('contacto_principal'),
                notas=request.POST.get('notas')
            )
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('lista_proveedores')
        except Exception as e:
            messages.error(request, f'Error al crear proveedor: {str(e)}')
    
    return render(request, 'proveedores/formulario.html')

@login_required
def detalle_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    
    if request.method == 'POST':
        proveedor.nombre = request.POST.get('nombre')
        proveedor.cuit = request.POST.get('cuit')
        proveedor.email = request.POST.get('email')
        proveedor.telefono = request.POST.get('telefono')
        proveedor.direccion = request.POST.get('direccion')
        proveedor.ciudad = request.POST.get('ciudad')
        proveedor.provincia = request.POST.get('provincia')
        proveedor.codigo_postal = request.POST.get('codigo_postal')
        proveedor.contacto_principal = request.POST.get('contacto_principal')
        proveedor.notas = request.POST.get('notas')
        proveedor.activo = request.POST.get('activo') == 'true'
        proveedor.save()
        
        messages.success(request, 'Proveedor actualizado exitosamente')
        return redirect('lista_proveedores')
    
    return render(request, 'proveedores/formulario.html', {'proveedor': proveedor})
