from django.urls import path
from . import views

urlpatterns = [
    path('operaciones-pendientes/', views.lista_operaciones_pendientes, name='lista_operaciones_pendientes'),
    path('operaciones-pendientes/<int:operacion_id>/procesar/', views.procesar_operacion, name='procesar_operacion'),
    path('sincronizar/', views.sincronizar_manual, name='sincronizar_manual'),
    path('logs/', views.lista_logs_sincronizacion, name='lista_logs_sincronizacion'),
]