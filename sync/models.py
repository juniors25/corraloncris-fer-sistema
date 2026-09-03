"""
Modelos para sistema de sincronización local-nube
"""
from django.db import models
from django.utils import timezone
import json

class OperacionPendiente(models.Model):
    """Operaciones que requieren sincronización cuando hay internet"""
    TIPO_OPERACION_CHOICES = [
        ('facturacion_arca', 'Facturación ARCA'),
        ('whatsapp', 'Envío WhatsApp'),
        ('venta_nube', 'Venta a nube'),
        ('producto_nube', 'Producto a nube'),
        ('cliente_nube', 'Cliente a nube'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    tipo_operacion = models.CharField(max_length=50, choices=TIPO_OPERACION_CHOICES)
    datos = models.JSONField()  # datos para procesar
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    intentos = models.IntegerField(default=0)
    mensaje_error = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Operación Pendiente'
        verbose_name_plural = 'Operaciones Pendientes'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_operacion_display()} - {self.estado}"
    
    def procesar(self):
        """Intentar procesar la operación"""
        from integraciones.arca import procesar_factura_arca
        from integraciones.whatsapp import enviar_mensaje_whatsapp
        
        try:
            self.estado = 'procesando'
            self.intentos += 1
            self.save()
            
            if self.tipo_operacion == 'facturacion_arca':
                venta_id = self.datos.get('venta_id')
                from ventas.models import Venta
                venta = Venta.objects.get(id=venta_id)
                exito, resultado = procesar_factura_arca(venta, usar_demo=False)
                
                if exito:
                    self.estado = 'completado'
                    self.fecha_procesamiento = timezone.now()
                else:
                    self.estado = 'error'
                    self.mensaje_error = resultado.get('error', 'Error desconocido')
                    
            elif self.tipo_operacion == 'whatsapp':
                numero = self.datos.get('numero')
                mensaje = self.datos.get('mensaje')
                exito = enviar_mensaje_whatsapp(numero, mensaje)
                
                if exito:
                    self.estado = 'completado'
                    self.fecha_procesamiento = timezone.now()
                else:
                    self.estado = 'error'
                    self.mensaje_error = 'Error al enviar mensaje WhatsApp'
            
            self.save()
            return self.estado == 'completado'
            
        except Exception as e:
            self.estado = 'error'
            self.mensaje_error = str(e)
            self.save()
            return False

class SincronizacionLog(models.Model):
    """Registro de sincronizaciones realizadas"""
    fecha = models.DateTimeField(auto_now_add=True)
    exitosa = models.BooleanField(default=True)
    operaciones_procesadas = models.IntegerField(default=0)
    operaciones_exitosas = models.IntegerField(default=0)
    operaciones_fallidas = models.IntegerField(default=0)
    duracion_segundos = models.FloatField(default=0)
    mensaje = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Log de Sincronización'
        verbose_name_plural = 'Logs de Sincronización'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Sincronización {self.fecha} - {'Exitosa' if self.exitosa else 'Fallida'}"