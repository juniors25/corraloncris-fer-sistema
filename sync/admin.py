from django.contrib import admin
from .models import OperacionPendiente, SincronizacionLog

@admin.register(OperacionPendiente)
class OperacionPendienteAdmin(admin.ModelAdmin):
    list_display = ['tipo_operacion', 'estado', 'intentos', 'fecha_creacion', 'fecha_procesamiento']
    list_filter = ['tipo_operacion', 'estado', 'fecha_creacion']
    search_fields = ['mensaje_error']
    readonly_fields = ['fecha_creacion', 'fecha_procesamiento']
    
    actions = ['procesar_seleccionados']
    
    def procesar_seleccionados(self, request, queryset):
        procesados = 0
        exitosos = 0
        for operacion in queryset:
            if operacion.procesar():
                exitosos += 1
            procesados += 1
        
        self.message_user(request, f'Procesadas {procesados} operaciones: {exitosos} exitosas, {procesados - exitosos} fallidas')
    
    procesar_seleccionados.short_description = 'Procesar operaciones seleccionadas'

@admin.register(SincronizacionLog)
class SincronizacionLogAdmin(admin.ModelAdmin):
    list_display = ['fecha', 'exitosa', 'operaciones_procesadas', 'operaciones_exitosas', 'operaciones_fallidas', 'duracion_segundos']
    list_filter = ['exitosa', 'fecha']
    readonly_fields = ['fecha', 'operaciones_procesadas', 'operaciones_exitosas', 'operaciones_fallidas', 'duracion_segundos', 'mensaje']