from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid

class Caja(models.Model):
    """Control de caja por turnos"""
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    vendedor = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='abierta')
    monto_apertura = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    monto_cierre = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Caja'
        verbose_name_plural = 'Cajas'
        ordering = ['-fecha_apertura']
    
    def __str__(self):
        return f"Caja #{self.numero} - {self.get_estado_display()}"
    
    @property
    def ventas_count(self):
        return self.ventas.count()
    
    @property
    def total_ventas(self):
        return self.ventas.aggregate(total=models.Sum('total'))['total'] or 0
    
    def cerrar(self, monto_real):
        """Cerrar caja y calcular diferencia"""
        total_ventas = self.total_ventas
        self.monto_cierre = monto_real
        self.diferencia = monto_real - total_ventas
        self.estado = 'cerrada'
        self.fecha_cierre = timezone.now()
        self.save()

class MovimientoCaja(models.Model):
    """Movimientos de caja (ingresos/egresos)"""
    TIPO_CHOICES = [
        ('venta', 'Venta'),
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
        ('retiro', 'Retiro'),
        ('apertura', 'Apertura'),
        ('cierre', 'Cierre'),
    ]
    
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    descripcion = models.TextField(blank=True)
    metodo_pago = models.CharField(max_length=50, blank=True)  # efectivo, tarjeta, transferencia
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Caja'
        verbose_name_plural = 'Movimientos de Caja'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()}: ${self.monto}"

class Vendedor(models.Model):
    """Control de vendedores y comisiones"""
    usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE)
    porcentaje_comision = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                          help_text='Porcentaje de comisión sobre ventas')
    meta_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                   help_text='Meta de ventas mensual')
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.porcentaje_comision}% comisión"
    
    @property
    def ventas_mes(self):
        from django.utils import timezone
        mes_actual = timezone.now().replace(day=1)
        return self.usuario.ventas.filter(
            created_at__gte=mes_actual,
            estado='confirmada'
        ).aggregate(total=models.Sum('total'))['total'] or 0
    
    @property
    def comision_mes(self):
        return self.ventas_mes * (self.porcentaje_comision / 100)

class Venta(models.Model):
    TIPO_VENTA_CHOICES = [
        ('local', 'Local'),
        ('online', 'Online'),
        ('presupuesto', 'Presupuesto'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    vendedor = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    caja = models.ForeignKey(Caja, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA_CHOICES, default='local')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    metodo_pago = models.CharField(max_length=50, blank=True)  # efectivo, tarjeta, transferencia, credito
    observaciones = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Para conversiones de presupuestos
    convertido_a_venta = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                          related_name='presupuesto_origen')
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Venta #{self.numero} - {self.estado}"
    
    def calcular_total(self):
        """Calcular total de la venta"""
        total = 0
        for detalle in self.items.all():
            total += detalle.subtotal
        self.subtotal = total
        self.total = total
        self.save()
    
    def convertir_a_venta(self):
        """Convertir presupuesto en venta"""
        if self.tipo_venta == 'presupuesto' and self.estado == 'borrador':
            self.tipo_venta = 'local'
            self.estado = 'confirmada'
            self.save()
            return True
        return False

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Para gestión de cortes
    longitud_corte = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                      help_text='Longitud de corte en metros (para productos que se cortan)')
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class PedidoOnline(models.Model):
    ESTADO_CHOICES = [
        ('recibido', 'Recibido'),
        ('procesando', 'Procesando'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='pedido_online')
    nombre_cliente = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    direccion_entrega = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recibido')
    numero_whatsapp = models.CharField(max_length=20, blank=True)
    mensaje_whatsapp_enviado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido Online'
        verbose_name_plural = 'Pedidos Online'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.venta.numero} - {self.nombre_cliente}"

class Acopio(models.Model):
    """Gestión de acopio (venta anticipada con entrega diferida)"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('parcialmente_entregado', 'Parcialmente Entregado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='acopio')
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='acopios')
    fecha_venta = models.DateField()
    fecha_entrega_estimada = models.DateField()
    fecha_entrega_real = models.DateField(null=True, blank=True)
    porcentaje_pendiente = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Acopio'
        verbose_name_plural = 'Acopios'
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Acopio #{self.venta.numero} - {self.cliente.nombre}"
    
    @property
    def cantidad_entregada(self):
        """Porcentaje ya entregado"""
        return 100 - self.porcentaje_pendiente
    
    def registrar_entrega_parcial(self, porcentaje):
        """Registrar entrega parcial"""
        self.porcentaje_pendiente -= porcentaje
        if self.porcentaje_pendiente <= 0:
            self.porcentaje_pendiente = 0
            self.estado = 'completado'
            self.fecha_entrega_real = timezone.now().date()
        elif self.porcentaje_pendiente < 100:
            self.estado = 'parcialmente_entregado'
        self.save()

class Factura(models.Model):
    TIPO_COMPROBANTE_CHOICES = [
        ('factura_a', 'Factura A'),
        ('factura_b', 'Factura B'),
        ('factura_c', 'Factura C'),
        ('remito', 'Remito'),
        ('recibo', 'Recibo'),
        ('nota_credito', 'Nota de Crédito'),
        ('nota_debito', 'Nota de Débito'),
    ]
    
    ESTADO_ARCA_CHOICES = [
        ('no_generado', 'No Generado'),
        ('pendiente', 'Pendiente'),
        ('generado', 'Generado'),
        ('error', 'Error'),
        ('anulado', 'Anulado'),
    ]
    
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='factura')
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE_CHOICES)
    numero_afip = models.CharField(max_length=50, blank=True)
    cae = models.CharField(max_length=20, blank=True)
    vencimiento_cae = models.DateField(blank=True, null=True)
    pdf_url = models.URLField(blank=True)
    xml_afip = models.TextField(blank=True)
    estado_arca = models.CharField(max_length=20, choices=ESTADO_ARCA_CHOICES, default='no_generado')
    mensaje_error = models.TextField(blank=True)
    es_remito_manual = models.BooleanField(default=False)  # Para remitos generados manualmente
    creado_por_usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_tipo_comprobante_display()} #{self.numero_afip or 'Pendiente'}"
    
    def generar_comprobante_manual(self, tipo, numero):
        """Generar comprobante manual (remito/factura) sin ARCA"""
        self.tipo_comprobante = tipo
        self.numero_afip = numero
        self.estado_arca = 'generado'
        self.es_remito_manual = True
        self.save()
        
        # Actualizar cliente si corresponde
        if self.venta.cliente:
            if tipo == 'remito':
                self.venta.cliente.ultimo_remito = numero
            else:
                self.venta.cliente.registrar_factura(numero, self.venta.total)
            self.venta.cliente.save()