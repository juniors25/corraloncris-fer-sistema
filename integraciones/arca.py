"""
Módulo de integración con sistema ARCA para facturación electrónica
Este módulo proporciona funciones para interactuar con la API de ARCA
"""

import requests
import json
from django.conf import settings
from datetime import datetime, timedelta

class ARCAIntegration:
    """Clase para manejar la integración con ARCA"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'ARCA_API_URL', 'https://api.arca.com.ar/v1')
        self.api_key = getattr(settings, 'ARCA_API_KEY', '')
        self.cuit = getattr(settings, 'ARCA_CUIT', '')
        self.punto_venta = getattr(settings, 'ARCA_PUNTO_VENTA', '0001')
        
    def authenticate(self):
        """Autenticar con el sistema ARCA"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            response = requests.post(
                f'{self.api_url}/auth',
                headers=headers,
                json={'cuit': self.cuit}
            )
            
            if response.status_code == 200:
                return response.json().get('token')
            else:
                raise Exception(f'Error de autenticación: {response.text}')
                
        except Exception as e:
            raise Exception(f'Error al conectar con ARCA: {str(e)}')
    
    def generar_factura(self, venta_data):
        """Generar una factura electrónica"""
        try:
            token = self.authenticate()
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.post(
                f'{self.api_url}/facturas',
                headers=headers,
                json=venta_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Error al generar factura: {response.text}')
                
        except Exception as e:
            raise Exception(f'Error en generación de factura: {str(e)}')
    
    def generar_factura_demo(self, venta_data):
        """Generar factura en modo demo (sin conexión real)"""
        """Esta función simula la respuesta de ARCA para pruebas"""
        from datetime import datetime
        import random
        
        # Simular número de comprobante AFIP
        fecha = datetime.now()
        numero_afip = f"{fecha.strftime('%Y%m%d')}{self.punto_venta}{random.randint(10000000, 99999999)}"
        
        # Simular CAE (Código de Autorización Electrónico)
        cae = f"{random.randint(10000000000000, 99999999999999)}"
        
        # Simular vencimiento del CAE (10 días)
        vencimiento_cae = (fecha + timedelta(days=10)).strftime('%Y-%m-%d')
        
        return {
            'success': True,
            'numero_afip': numero_afip,
            'cae': cae,
            'vencimiento_cae': vencimiento_cae,
            'fecha_generacion': fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'estado': 'generado'
        }
    
    def consultar_factura(self, numero_afip):
        """Consultar estado de una factura existente"""
        try:
            token = self.authenticate()
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.get(
                f'{self.api_url}/facturas/{numero_afip}',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Error al consultar factura: {response.text}')
                
        except Exception as e:
            raise Exception(f'Error en consulta de factura: {str(e)}')
    
    def anular_factura(self, numero_afip):
        """Anular una factura existente"""
        try:
            token = self.authenticate()
            
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            response = requests.delete(
                f'{self.api_url}/facturas/{numero_afip}',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Error al anular factura: {response.text}')
                
        except Exception as e:
            raise Exception(f'Error en anulación de factura: {str(e)}')


def preparar_datos_factura(venta, cliente=None):
    """Preparar los datos de una venta para el formato de ARCA"""
    from ventas.models import DetalleVenta
    
    items = []
    for detalle in venta.items.all():
        items.append({
            'codigo': detalle.producto.codigo_barras or '',
            'descripcion': detalle.producto.nombre,
            'cantidad': detalle.cantidad,
            'precio_unitario': float(detalle.precio_unitario),
            'subtotal': float(detalle.subtotal)
        })
    
    datos_factura = {
        'tipo_comprobante': venta.factura.tipo_comprobante if hasattr(venta, 'factura') else 'factura_b',
        'fecha': venta.created_at.strftime('%Y-%m-%d'),
        'importe_total': float(venta.total),
        'importe_gravado': float(venta.subtotal),
        'importe_no_gravado': 0.0,
        'moneda': 'ARS',
        'items': items
    }
    
    if cliente:
        datos_factura.update({
            'cliente_tipo_documento': cliente.tipo_documento,
            'cliente_numero_documento': cliente.numero_documento,
            'cliente_nombre': cliente.nombre,
            'cliente_direccion': cliente.direccion,
            'cliente_ciudad': cliente.ciudad,
            'cliente_provincia': cliente.provincia,
            'cliente_codigo_postal': cliente.codigo_postal
        })
    
    return datos_factura

def procesar_factura_arca(venta, usar_demo=True):
    """
    Procesar una factura con ARCA (modo demo por defecto)
    Devuelve True si se procesó correctamente, False en caso contrario
    """
    try:
        arca = ARCAIntegration()
        
        # Preparar datos de la factura
        cliente = venta.cliente if hasattr(venta, 'cliente') else None
        datos_factura = preparar_datos_factura(venta, cliente)
        
        # Generar factura (demo o real)
        if usar_demo:
            resultado = arca.generar_factura_demo(datos_factura)
        else:
            resultado = arca.generar_factura(datos_factura)
        
        if resultado.get('success'):
            # Actualizar la factura en el sistema
            venta.factura.numero_afip = resultado['numero_afip']
            venta.factura.cae = resultado['cae']
            venta.factura.vencimiento_cae = resultado['vencimiento_cae']
            venta.factura.estado_arca = 'generado'
            venta.factura.save()
            
            # Si hay cliente, actualizar su información
            if cliente:
                from clientes.models import FacturaCliente
                # Crear registro de factura de cliente
                factura_cliente = FacturaCliente.objects.create(
                    cliente=cliente,
                    tipo_comprobante=venta.factura.tipo_comprobante,
                    numero_comprobante=resultado['numero_afip'],
                    fecha_emision=venta.created_at.date(),
                    monto_total=venta.total,
                    estado='pendiente',
                    vinculada_arca=True,
                    numero_afip=resultado['numero_afip']
                )
                # Actualizar saldo deudor del cliente
                cliente.registrar_factura(resultado['numero_afip'], venta.total)
            
            return True, resultado
        else:
            venta.factura.estado_arca = 'error'
            venta.factura.mensaje_error = resultado.get('error', 'Error desconocido')
            venta.factura.save()
            return False, resultado
            
    except Exception as e:
        venta.factura.estado_arca = 'error'
        venta.factura.mensaje_error = str(e)
        venta.factura.save()
        return False, {'error': str(e)}