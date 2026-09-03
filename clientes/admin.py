from django.contrib import admin
from .models import Cliente, FacturaCliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado_credito', 'saldo_deudor', 'limite_credito', 'ultima_factura', 'telefono', 'activo']
    list_filter = ['activo', 'estado_credito', 'tipo_documento', 'created_at']
    search_fields = ['nombre', 'numero_documento', 'telefono', 'email']
    list_editable = ['activo']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'tipo_documento', 'numero_documento', 'email', 'telefono')
        }),
        ('Dirección', {
            'fields': ('direccion', 'ciudad', 'provincia', 'codigo_postal')
        }),
        ('Sistema de Crédito y Facturación', {
            'fields': ('estado_credito', 'limite_credito', 'saldo_deudor', 'ultima_factura', 'ultimo_remito')
        }),
        ('Información Adicional', {
            'fields': ('activo', 'notas')
        }),
    )
    
    readonly_fields = ['estado_credito']

@admin.register(FacturaCliente)
class FacturaClienteAdmin(admin.ModelAdmin):
    list_display = ['numero_comprobante', 'tipo_comprobante', 'cliente', 'fecha_emision', 'monto_original', 'saldo_pendiente', 'estado', 'vinculada_arca']
    list_filter = ['tipo_comprobante', 'estado', 'vinculada_arca', 'fecha_emision']
    search_fields = ['numero_comprobante', 'cliente__nombre', 'numero_afip']
    readonly_fields = ['saldo_pendiente', 'esta_vencida']
    
    fieldsets = (
        ('Información del Comprobante', {
            'fields': ('cliente', 'tipo_comprobante', 'numero_comprobante', 'numero_afip')
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento')
        }),
        ('Montos', {
            'fields': ('monto_original', 'monto_ajustado', 'monto_pagado')
        }),
        ('Estado y Vinculación', {
            'fields': ('estado', 'vinculada_arca')
        }),
        ('Información Adicional', {
            'fields': ('observaciones',)
        }),
    )
