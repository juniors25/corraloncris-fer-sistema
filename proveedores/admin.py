from django.contrib import admin
from .models import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cuit', 'telefono', 'email', 'activo']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'cuit', 'telefono', 'email']
    list_editable = ['activo']
