from django.urls import path
from . import views

urlpatterns = [
    path('nueva/', views.nueva_venta, name='nueva_venta'),
    path('presupuesto/', views.crear_presupuesto, name='crear_presupuesto'),
    path('presupuestos/', views.lista_presupuestos, name='lista_presupuestos'),
    path('presupuesto/<int:presupuesto_id>/convertir/', views.convertir_presupuesto_a_venta, name='convertir_presupuesto'),
    path('pos/', views.pos_tactil, name='pos_tactil'),
    path('online/', views.pedido_online, name='pedido_online'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('imprimir/<int:venta_id>/', views.imprimir_factura, name='imprimir_factura'),
]