from django.contrib import admin
from .models import Categoria, Producto, MovimientoStock

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'created_at']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_barras', 'categoria', 'precio_venta', 'stock_actual', 'activo', 'stock_bajo']
    list_filter = ['categoria', 'activo', 'created_at']
    search_fields = ['nombre', 'codigo_barras', 'codigo_qr']
    list_editable = ['activo']
    readonly_fields = ['stock_bajo']

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'fecha', 'motivo']
    list_filter = ['tipo', 'fecha']
    search_fields = ['producto__nombre']
    readonly_fields = ['fecha']
