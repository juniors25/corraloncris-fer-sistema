import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from productos.models import Categoria, Producto, MovimientoStock

# Crear categorías
categorias_data = [
    {'nombre': 'Herramientas Manuales', 'descripcion': 'Martillos, destornilladores, llaves, etc.'},
    {'nombre': 'Herramientas Eléctricas', 'descripcion': 'Taladros, sierras, amoladoras, etc.'},
    {'nombre': 'Pinturas y Accesorios', 'descripcion': 'Pinturas, brochas, rodillos, etc.'},
    {'nombre': 'Plomería', 'descripcion': 'Caños, grifería, accesorios de baño y cocina'},
    {'nombre': 'Electricidad', 'descripcion': 'Cables, interruptores, iluminación'},
    {'nombre': 'Construcción', 'descripcion': 'Cemento, arena, ladrillos, herramientas de construcción'},
    {'nombre': 'Jardinería', 'descripcion': 'Herramientas de jardín, plantas, riego'},
    {'nombre': 'Ferretería General', 'descripcion': 'Clavos, tornillos, bisagras, cerraduras'},
]

print("Creando categorías...")
for cat_data in categorias_data:
    categoria, created = Categoria.objects.get_or_create(
        nombre=cat_data['nombre'],
        defaults={'descripcion': cat_data['descripcion']}
    )
    if created:
        print(f"[OK] Categoría creada: {categoria.nombre}")
    else:
        print(f"[EXISTENTE] Categoría existente: {categoria.nombre}")

# Crear productos
productos_data = [
    # Herramientas Manuales
    {'nombre': 'Martillo Carpintero 500g', 'categoria': 'Herramientas Manuales', 'precio_costo': 2500, 'precio_venta': 4500, 'stock': 50, 'codigo_barras': '779123456001'},
    {'nombre': 'Destornillador Phillips #2', 'categoria': 'Herramientas Manuales', 'precio_costo': 800, 'precio_venta': 1500, 'stock': 100, 'codigo_barras': '779123456002'},
    {'nombre': 'Llave Inglesa 8"', 'categoria': 'Herramientas Manuales', 'precio_costo': 3000, 'precio_venta': 5500, 'stock': 30, 'codigo_barras': '779123456003'},
    {'nombre': 'Juego de Llaves 6 pzas', 'categoria': 'Herramientas Manuales', 'precio_costo': 8000, 'precio_venta': 15000, 'stock': 25, 'codigo_barras': '779123456004'},
    
    # Herramientas Eléctricas
    {'nombre': 'Taladro Percutor 500W', 'categoria': 'Herramientas Eléctricas', 'precio_costo': 15000, 'precio_venta': 28000, 'stock': 15, 'codigo_barras': '779123456005'},
    {'nombre': 'Sierra Circular 7-1/4"', 'categoria': 'Herramientas Eléctricas', 'precio_costo': 25000, 'precio_venta': 45000, 'stock': 10, 'codigo_barras': '779123456006'},
    {'nombre': 'Amoladora 4-1/2"', 'categoria': 'Herramientas Eléctricas', 'precio_costo': 12000, 'precio_venta': 22000, 'stock': 20, 'codigo_barras': '779123456007'},
    
    # Pinturas
    {'nombre': 'Pintura Interior 20L Blanco', 'categoria': 'Pinturas y Accesorios', 'precio_costo': 15000, 'precio_venta': 28000, 'stock': 30, 'codigo_barras': '779123456008'},
    {'nombre': 'Rodillo Pared 18cm', 'categoria': 'Pinturas y Accesorios', 'precio_costo': 2000, 'precio_venta': 4000, 'stock': 80, 'codigo_barras': '779123456009'},
    {'nombre': 'Brocha 2" Pelo Sintético', 'categoria': 'Pinturas y Accesorios', 'precio_costo': 500, 'precio_venta': 1200, 'stock': 150, 'codigo_barras': '779123456010'},
    
    # Plomería
    {'nombre': 'Caño PVC 3m 1/2"', 'categoria': 'Plomería', 'precio_costo': 800, 'precio_venta': 1500, 'stock': 200, 'codigo_barras': '779123456011'},
    {'nombre': 'Grifería Lavatorio Cromo', 'categoria': 'Plomería', 'precio_costo': 8000, 'precio_venta': 15000, 'stock': 25, 'codigo_barras': '779123456012'},
    {'nombre': 'Tanque 200L', 'categoria': 'Plomería', 'precio_costo': 25000, 'precio_venta': 45000, 'stock': 15, 'codigo_barras': '779123456013'},
    
    # Electricidad
    {'nombre': 'Cable 2.5mm 100m', 'categoria': 'Electricidad', 'precio_costo': 8000, 'precio_venta': 15000, 'stock': 50, 'codigo_barras': '779123456014'},
    {'nombre': 'Interruptor Termomagnético 2x20A', 'categoria': 'Electricidad', 'precio_costo': 3000, 'precio_venta': 6000, 'stock': 40, 'codigo_barras': '779123456015'},
    {'nombre': 'Led Panel 12W', 'categoria': 'Electricidad', 'precio_costo': 2000, 'precio_venta': 4000, 'stock': 60, 'codigo_barras': '779123456016'},
    
    # Construcción
    {'nombre': 'Cemento 50kg', 'categoria': 'Construcción', 'precio_costo': 1200, 'precio_venta': 2500, 'stock': 100, 'codigo_barras': '779123456017'},
    {'nombre': 'Arena 1m³', 'categoria': 'Construcción', 'precio_costo': 5000, 'precio_venta': 10000, 'stock': 20, 'codigo_barras': '779123456018'},
    {'nombre': 'Ladrillo Común 1000u', 'categoria': 'Construcción', 'precio_costo': 8000, 'precio_venta': 15000, 'stock': 30, 'codigo_barras': '779123456019'},
    
    # Jardinería
    {'nombre': 'Macheta 18"', 'categoria': 'Jardinería', 'precio_costo': 1500, 'precio_venta': 3000, 'stock': 40, 'codigo_barras': '779123456020'},
    {'nombre': 'Manguera 20m 1/2"', 'categoria': 'Jardinería', 'precio_costo': 3000, 'precio_venta': 6000, 'stock': 35, 'codigo_barras': '779123456021'},
    
    # Ferretería General
    {'nombre': 'Clavos 1kg 1"', 'categoria': 'Ferretería General', 'precio_costo': 800, 'precio_venta': 1500, 'stock': 150, 'codigo_barras': '779123456022'},
    {'nombre': 'Tornillos 1kg 1/2"', 'categoria': 'Ferretería General', 'precio_costo': 1000, 'precio_venta': 2000, 'stock': 120, 'codigo_barras': '779123456023'},
    {'nombre': 'Bisagra 3" x12u', 'categoria': 'Ferretería General', 'precio_costo': 2000, 'precio_venta': 4000, 'stock': 80, 'codigo_barras': '779123456024'},
    {'nombre': 'Cerradura Punto 3LL', 'categoria': 'Ferretería General', 'precio_costo': 3500, 'precio_venta': 7000, 'stock': 60, 'codigo_barras': '779123456025'},
]

print("\nCreando productos...")
for prod_data in productos_data:
    categoria = Categoria.objects.get(nombre=prod_data['categoria'])
    
    producto, created = Producto.objects.get_or_create(
        codigo_barras=prod_data['codigo_barras'],
        defaults={
            'nombre': prod_data['nombre'],
            'categoria': categoria,
            'precio_costo': prod_data['precio_costo'],
            'precio_venta': prod_data['precio_venta'],
            'stock_actual': prod_data['stock'],
            'stock_minimo': 5,
            'unidad_medida': 'unidad',
            'activo': True
        }
    )
    
    if created:
        # Crear movimiento de stock inicial
        MovimientoStock.objects.create(
            producto=producto,
            tipo='entrada',
            cantidad=prod_data['stock'],
            motivo='Stock inicial'
        )
        print(f"[OK] Producto creado: {producto.nombre} - Stock: {producto.stock_actual}")
    else:
        print(f"[EXISTENTE] Producto existente: {producto.nombre} - Stock: {producto.stock_actual}")

print(f"\n[COMPLETADO] Carga completada!")
print(f"Total categorías: {Categoria.objects.count()}")
print(f"Total productos: {Producto.objects.count()}")
print(f"Valor inventario: ${sum(p.precio_costo * p.stock_actual for p in Producto.objects.all()):,.2f}")