from django.db import models
from django.core.validators import MinValueValidator
from clientes.models import Cliente

class Venta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    TIPO_VENTA_CHOICES = [
        ('local', 'Venta Local'),
        ('online', 'Venta Online'),
    ]
    
    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA_CHOICES, default='local')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Venta #{self.numero} - ${self.total}"
    
    def calcular_total(self):
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal - self.descuento
        self.save()

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

class PedidoOnline(models.Model):
    ESTADO_CHOICES = [
        ('recibido', 'Recibido'),
        ('procesando', 'Procesando'),
        ('listo', 'Listo para Retiro'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='pedido_online')
    nombre_cliente = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    direccion_entrega = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='recibido')
    fecha_entrega_estimada = models.DateTimeField(blank=True, null=True)
    numero_whatsapp = models.CharField(max_length=20, blank=True)
    mensaje_whatsapp_enviado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido Online'
        verbose_name_plural = 'Pedidos Online'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Pedido #{self.venta.numero} - {self.nombre_cliente}"

class Factura(models.Model):
    TIPO_COMPROBANTE_CHOICES = [
        ('factura_a', 'Factura A'),
        ('factura_b', 'Factura B'),
        ('factura_c', 'Factura C'),
        ('remito', 'Remito'),
        ('recibo', 'Recibo'),
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
