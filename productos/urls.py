from django.urls import path
from . import views, mobile_views, api_views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('escanear/', views.escanear_producto, name='escanear_producto'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    # Rutas para escaneo móvil web
    path('escaneo-movil/', mobile_views.escaneo_movil, name='escaneo_movil'),
    path('api/procesar-escaneo/', mobile_views.procesar_escaneo_movil, name='procesar_escaneo_movil'),
    path('api/actualizar-stock/', mobile_views.actualizar_stock_movil, name='actualizar_stock_movil'),
    # API REST para app móvil dedicada
    path('api/v1/productos/', api_views.api_productos, name='api_productos'),
    path('api/v1/producto/codigo/', api_views.api_producto_por_codigo, name='api_producto_por_codigo'),
    path('api/v1/stock/actualizar/', api_views.api_actualizar_stock, name='api_actualizar_stock'),
    path('api/v1/stock/movimientos/', api_views.api_movimientos_stock, name='api_movimientos_stock'),
    path('api/v1/estadisticas/', api_views.api_estadisticas, name='api_estadisticas'),
]