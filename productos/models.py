from django.db import models
from django.core.validators import MinValueValidator

class Deposito(models.Model):
    """Múltiples depósitos/sucursales"""
    TIPO_CHOICES = [
        ('sucursal', 'Sucursal'),
        ('deposito', 'Depósito'),
        ('taller', 'Taller'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='deposito')
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    encargado = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class StockDeposito(models.Model):
    """Stock por depósito"""
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='stocks_deposito')
    deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE, related_name='stocks')
    cantidad = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    ubicacion = models.CharField(max_length=100, blank=True, help_text='Ubicación específica en el depósito')
    
    class Meta:
        verbose_name = 'Stock por Depósito'
        verbose_name_plural = 'Stocks por Depósito'
        unique_together = ['producto', 'deposito']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.deposito.nombre}: {self.cantidad}"

class TransferenciaStock(models.Model):
    """Transferencias entre depósitos"""
    TIPO_CHOICES = [
        ('transferencia', 'Transferencia'),
        ('ajuste', 'Ajuste'),
        ('venta', 'Venta'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_transito', 'En Tránsito'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='transferencias')
    deposito_origen = models.ForeignKey(Deposito, on_delete=models.CASCADE, related_name='transferencias_salida')
    deposito_destino = models.ForeignKey(Deposito, on_delete=models.CASCADE, related_name='transferencias_entrada')
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='transferencia')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True)
    solicitado_por = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Transferencia de Stock'
        verbose_name_plural = 'Transferencias de Stock'
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Transferencia #{self.numero} - {self.producto.nombre}"
    
    def procesar(self):
        """Procesar la transferencia"""
        if self.estado == 'pendiente':
            # Restar del depósito origen
            stock_origen = StockDeposito.objects.get(
                producto=self.producto,
                deposito=self.deposito_origen
            )
            stock_origen.cantidad -= self.cantidad
            stock_origen.save()
            
            # Sumar al depósito destino
            stock_destino, created = StockDeposito.objects.get_or_create(
                producto=self.producto,
                deposito=self.deposito_destino,
                defaults={'cantidad': 0}
            )
            stock_destino.cantidad += self.cantidad
            stock_destino.save()
            
            # Actualizar stock total del producto
            self.producto.actualizar_stock(0)  # Recalcular total
            
            self.estado = 'completado'
            self.fecha_completado = timezone.now()
            self.save()
            return True
        return False

class KitProducto(models.Model):
    """Kits de productos (productos compuestos)"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Kit de Producto'
        verbose_name_plural = 'Kits de Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def precio_kit(self):
        """Precio total del kit"""
        total = 0
        for item in self.items.all():
            total += item.producto.precio_venta * item.cantidad
        return total

class ItemKit(models.Model):
    """Productos que componen un kit"""
    kit = models.ForeignKey(KitProducto, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        verbose_name = 'Item de Kit'
        verbose_name_plural = 'Items de Kit'
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class ProductoEquivalente(models.Model):
    """Productos equivalentes/sustitutos"""
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='equivalentes')
    equivalente = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='sustitutos')
    prioridad = models.IntegerField(default=1, help_text='Prioridad de sustitución (1 es el más alto)')
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Producto Equivalente'
        verbose_name_plural = 'Productos Equivalentes'
        unique_together = ['producto', 'equivalente']
    
    def __str__(self):
        return f"{self.producto.nombre} → {self.equivalente.nombre}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class ListaPrecios(models.Model):
    """Múltiples listas de precios (menudeo, mayorista, contratistas)"""
    TIPO_CHOICES = [
        ('menudeo', 'Menudeo'),
        ('mayorista', 'Mayorista'),
        ('contratista', 'Contratista'),
        ('obra', 'Obra'),
        ('promocional', 'Promocional'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='menudeo')
    descripcion = models.TextField(blank=True)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                          help_text='Porcentaje de descuento sobre precio base')
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lista de Precios'
        verbose_name_plural = 'Listas de Precios'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

class PrecioLista(models.Model):
    """Precio específico de un producto en una lista"""
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE, related_name='precios_lista')
    lista = models.ForeignKey(ListaPrecios, on_delete=models.CASCADE, related_name='precios')
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    vigente_desde = models.DateField()
    vigente_hasta = models.DateField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Precio de Lista'
        verbose_name_plural = 'Precios de Lista'
        unique_together = ['producto', 'lista', 'vigente_desde']
        ordering = ['-vigente_desde']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.lista.nombre}: ${self.precio}"

class Producto(models.Model):
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)
    codigo_qr = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    deposito_principal = models.ForeignKey(Deposito, on_delete=models.SET_NULL, null=True, blank=True, 
                                       related_name='productos')
    precio_costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock_actual = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.IntegerField(default=5, validators=[MinValueValidator(0)])
    
    # Unidades de medida mejoradas
    unidad_medida = models.CharField(max_length=20, default='unidad', 
                                     help_text='Unidad base: unidad, metro, kg, litro, caja')
    unidad_medida_venta = models.CharField(max_length=20, default='unidad',
                                          help_text='Unidad de venta: unidad, metro, kg, litro, caja')
    factor_conversion = models.DecimalField(max_digits=10, decimal_places=4, default=1.0,
                                          help_text='Factor de conversión de unidad base a unidad de venta')
    
    # Gestión de cortes (para barras, tubos, etc.)
    permite_cortes = models.BooleanField(default=False,
                                       help_text='Permite venta por longitud (barras, tubos)')
    longitud_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     help_text='Longitud total en metros (para productos que se cortan)')
    
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock_actual} {self.unidad_medida_venta}"
    
    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo
    
    @property
    def stock_disponible(self):
        """Stock disponible en unidad de venta"""
        return int(self.stock_actual / self.factor_conversion) if self.factor_conversion > 0 else self.stock_actual
    
    @property
    def equivalentes_disponibles(self):
        """Obtener productos equivalentes con stock"""
        equivalentes = []
        for eq in self.equivalentes.filter(activo=True):
            if eq.equivalente.stock_actual > 0:
                equivalentes.append(eq.equivalente)
        return equivalentes
    
    def obtener_precio_lista(self, lista_precios):
        """Obtener precio de una lista específica"""
        from django.utils import timezone
        hoy = timezone.now().date()
        
        precio_lista = self.precios_lista.filter(
            lista=lista_precios,
            vigente_desde__lte=hoy
        ).filter(
            models.Q(vigente_hasta__isnull=True) | models.Q(vigente_hasta__gte=hoy)
        ).first()
        
        if precio_lista:
            return precio_lista.precio
        
        # Si no hay precio específico, aplicar descuento de la lista
        if lista_precios.porcentaje_descuento > 0:
            return self.precio_venta * (1 - lista_precios.porcentaje_descuento / 100)
        
        return self.precio_venta
    
    def actualizar_stock(self, cantidad):
        """Actualizar stock considerando factor de conversión"""
        # Convertir cantidad a unidad base
        cantidad_base = cantidad * self.factor_conversion
        self.stock_actual += cantidad_base
        self.save()
    
    def convertir_a_unidad_venta(self, cantidad_base):
        """Convertir cantidad base a unidad de venta"""
        return cantidad_base / self.factor_conversion if self.factor_conversion > 0 else cantidad_base

class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('transferencia', 'Transferencia'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    motivo = models.TextField(blank=True)
    deposito = models.ForeignKey(Deposito, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.get_tipo_display()}: {self.cantidad}"