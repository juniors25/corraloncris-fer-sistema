from django.contrib import admin
from .models import Venta, DetalleVenta, PedidoOnline, Factura

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['subtotal']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'tipo_venta', 'estado', 'total', 'created_at']
    list_filter = ['estado', 'tipo_venta', 'created_at']
    search_fields = ['numero', 'cliente__nombre']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DetalleVentaInline]

@admin.register(PedidoOnline)
class PedidoOnlineAdmin(admin.ModelAdmin):
    list_display = ['venta', 'nombre_cliente', 'telefono', 'estado', 'created_at']
    list_filter = ['estado', 'created_at']
    search_fields = ['nombre_cliente', 'telefono', 'venta__numero']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'tipo_comprobante', 'numero_afip', 'estado_arca', 'created_at']
    list_filter = ['tipo_comprobante', 'estado_arca', 'created_at']
    search_fields = ['numero_afip', 'venta__numero']
    readonly_fields = ['created_at', 'updated_at']
