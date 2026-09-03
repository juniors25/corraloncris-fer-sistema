from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Cliente(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('dni', 'DNI'),
        ('cuil', 'CUIL'),
        ('cuit', 'CUIT'),
    ]
    
    ESTADO_CREDITO_CHOICES = [
        ('normal', 'Normal'),
        ('alerta', 'Alerta'),
        ('moroso', 'Moroso'),
        ('bloqueado', 'Bloqueado'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, blank=True)
    numero_documento = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    # Sistema de crédito y facturación
    estado_credito = models.CharField(max_length=20, choices=ESTADO_CREDITO_CHOICES, default='normal')
    limite_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    saldo_deudor = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    ultima_factura = models.CharField(max_length=50, blank=True)
    ultimo_remito = models.CharField(max_length=50, blank=True)
    
    # Ajuste por inflación
    indice_inflacion_base = models.DecimalField(max_digits=10, decimal_places=4, default=1.0,
                                            help_text='Índice de inflación base para ajuste de saldos')
    fecha_ajuste_inflacion = models.DateField(null=True, blank=True)
    
    activo = models.BooleanField(default=True)
    notas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.telefono}"
    
    @property
    def esta_moroso(self):
        """Verificar si el cliente está moroso según el saldo deudor"""
        return self.saldo_deudor > self.limite_credito
    
    @property
    def porcentaje_deuda(self):
        """Calcular porcentaje de deuda sobre el límite de crédito"""
        if self.limite_credito > 0:
            return (self.saldo_deudor / self.limite_credito) * 100
        return 0
    
    @property
    def saldo_deudor_ajustado(self):
        """Saldo deudor ajustado por inflación"""
        if self.indice_inflacion_base > 1.0:
            return self.saldo_deudor * self.indice_inflacion_base
        return self.saldo_deudor
    
    def actualizar_estado_credito(self):
        """Actualizar el estado de crédito según el saldo deudor"""
        porcentaje = self.porcentaje_deuda
        
        if porcentaje >= 100:
            self.estado_credito = 'bloqueado'
        elif porcentaje >= 80:
            self.estado_credito = 'moroso'
        elif porcentaje >= 50:
            self.estado_credito = 'alerta'
        else:
            self.estado_credito = 'normal'
        
        self.save()
    
    def actualizar_indice_inflacion(self, nuevo_indice):
        """Actualizar índice de inflación y ajustar saldos"""
        if self.indice_inflacion_base > 0:
            # Calcular factor de ajuste
            factor_ajuste = nuevo_indice / self.indice_inflacion_base
            
            # Ajustar saldo deudor
            self.saldo_deudor = self.saldo_deudor * factor_ajuste
            
            # Actualizar índice
            self.indice_inflacion_base = nuevo_indice
            self.fecha_ajuste_inflacion = timezone.now().date()
            
            self.save()
            return True
        return False
    
    def registrar_factura(self, numero_factura, monto):
        """Registrar una nueva factura y actualizar saldo deudor"""
        self.ultima_factura = numero_factura
        self.saldo_deudor += monto
        self.actualizar_estado_credito()
    
    def registrar_pago(self, monto):
        """Registrar un pago y actualizar saldo deudor"""
        self.saldo_deudor -= monto
        if self.saldo_deudor < 0:
            self.saldo_deudor = 0
        self.actualizar_estado_credito()

class FacturaCliente(models.Model):
    """Historial de facturas y remitos de clientes"""
    TIPO_COMPROBANTE_CHOICES = [
        ('factura', 'Factura'),
        ('remito', 'Remito'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('anulada', 'Anulada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='facturas')
    tipo_comprobante = models.CharField(max_length=20, choices=TIPO_COMPROBANTE_CHOICES)
    numero_comprobante = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(blank=True, null=True)
    monto_original = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    monto_ajustado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text='Monto ajustado por inflación')
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    vinculada_arca = models.BooleanField(default=False)
    numero_afip = models.CharField(max_length=50, blank=True)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Factura de Cliente'
        verbose_name_plural = 'Facturas de Clientes'
        ordering = ['-fecha_emision', '-created_at']
    
    def __str__(self):
        return f"{self.get_tipo_comprobante_display()} {self.numero_comprobante} - {self.cliente.nombre}"
    
    @property
    def saldo_pendiente(self):
        """Calcular saldo pendiente de pago (usando monto ajustado si existe)"""
        monto_a_usar = self.monto_ajustado if self.monto_ajustado else self.monto_original
        return monto_a_usar - self.monto_pagado
    
    @property
    def esta_vencida(self):
        """Verificar si la factura está vencida"""
        if self.fecha_vencimiento and self.estado == 'pendiente':
            return timezone.now().date() > self.fecha_vencimiento
        return False
    
    def ajustar_por_inflacion(self, factor_inflacion):
        """Ajustar monto por inflación"""
        if self.monto_ajustado is None:
            self.monto_ajustado = self.monto_original * factor_inflacion
        else:
            self.monto_ajustado = self.monto_ajustado * factor_inflacion
        self.save()
    
    def registrar_pago(self, monto):
        """Registrar un pago parcial o total"""
        self.monto_pagado += monto
        monto_a_usar = self.monto_ajustado if self.monto_ajustado else self.monto_original
        if self.monto_pagado >= monto_a_usar:
            self.estado = 'pagada'
            self.monto_pagado = monto_a_usar
        self.save()
        
        # Actualizar saldo deudor del cliente
        self.cliente.registrar_pago(monto)
