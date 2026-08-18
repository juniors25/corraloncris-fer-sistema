from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard_reportes'),
    path('ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('productos/', views.reporte_productos, name='reporte_productos'),
    path('clientes/', views.reporte_clientes, name='reporte_clientes'),
    path('pedidos-online/', views.reporte_pedidos_online, name='reporte_pedidos_online'),
]