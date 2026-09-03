from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import OperacionPendiente, SincronizacionLog
import time

@login_required
def lista_operaciones_pendientes(request):
    """Lista de operaciones pendientes de sincronización"""
    operaciones = OperacionPendiente.objects.filter(estado='pendiente').order_by('-fecha_creacion')
    return render(request, 'sync/lista_operaciones_pendientes.html', {'operaciones': operaciones})

@login_required
def procesar_operacion(request, operacion_id):
    """Procesar una operación pendiente individual"""
    operacion = OperacionPendiente.objects.get(id=operacion_id)
    
    if operacion.procesar():
        messages.success(request, f'Operación {operacion.get_tipo_operacion_display()} procesada exitosamente')
    else:
        messages.error(request, f'Error al procesar operación: {operacion.mensaje_error}')
    
    return redirect('lista_operaciones_pendientes')

@login_required
def sincronizar_manual(request):
    """Sincronización manual de todas las operaciones pendientes"""
    operaciones = OperacionPendiente.objects.filter(estado='pendiente')
    
    if not operaciones.exists():
        messages.info(request, 'No hay operaciones pendientes para sincronizar')
        return redirect('lista_operaciones_pendientes')
    
    inicio = time.time()
    exitosas = 0
    fallidas = 0
    
    for operacion in operaciones:
        if operacion.procesar():
            exitosas += 1
        else:
            fallidas += 1
    
    duracion = time.time() - inicio
    
    # Crear log de sincronización
    SincronizacionLog.objects.create(
        exitosa=(fallidas == 0),
        operaciones_procesadas=operaciones.count(),
        operaciones_exitosas=exitosas,
        operaciones_fallidas=fallidas,
        duracion_segundos=duracion,
        mensaje=f'Sincronización manual: {exitosas} exitosas, {fallidas} fallidas'
    )
    
    if fallidas == 0:
        messages.success(request, f'Sincronización completada: {exitosas} operaciones procesadas')
    else:
        messages.warning(request, f'Sincronización parcial: {exitosas} exitosas, {fallidas} fallidas')
    
    return redirect('lista_operaciones_pendientes')

@login_required
def lista_logs_sincronizacion(request):
    """Lista de logs de sincronización"""
    logs = SincronizacionLog.objects.all().order_by('-fecha')
    return render(request, 'sync/lista_logs_sincronizacion.html', {'logs': logs})