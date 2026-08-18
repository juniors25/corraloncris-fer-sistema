"""
Módulo de integración con WhatsApp Business API
Este módulo proporciona funciones para enviar mensajes de WhatsApp
"""

import requests
import json
from django.conf import settings

class WhatsAppIntegration:
    """Clase para manejar la integración con WhatsApp"""
    
    def __init__(self):
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
        
    def enviar_mensaje_texto(self, telefono, mensaje):
        """Enviar un mensaje de texto simple"""
        try:
            # Normalizar número de teléfono (formato internacional)
            telefono_normalizado = self._normalizar_telefono(telefono)
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messaging_product': 'whatsapp',
                'to': telefono_normalizado,
                'type': 'text',
                'text': {
                    'body': mensaje
                }
            }
            
            response = requests.post(
                f'{self.api_url}/{self.phone_number_id}/messages',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'Error al enviar mensaje: {response.text}')
                
        except Exception as e:
            raise Exception(f'Error en envío de WhatsApp: {str(e)}')
    
    def enviar_mensaje_pedido_confirmado(self, pedido):
        """Enviar mensaje de confirmación de pedido"""
        mensaje = f"""
🔔 *PEDIDO CONFIRMADO* 🔔

Hola {pedido.nombre_cliente},

Tu pedido #{pedido.venta.numero} ha sido confirmado.

📦 *Productos:*
"""
        for item in pedido.venta.items.all():
            mensaje += f"• {item.producto.nombre} x{item.cantidad} - ${item.subtotal}\n"
        
        mensaje += f"""
💰 *Total: ${pedido.venta.total}*

📍 *Dirección de entrega:*
{pedido.direccion_entrega or 'Retiro en local'}

📞 *Contacto:*
{pedido.telefono}

Te notificaremos cuando tu pedido esté listo para entrega.

¡Gracias por tu compra! 🛒
"""
        return self.enviar_mensaje_texto(pedido.telefono, mensaje)
    
    def enviar_mensaje_pedido_listo(self, pedido):
        """Enviar mensaje cuando el pedido está listo"""
        mensaje = f"""
✅ *PEDIDO LISTO PARA RETIRO* ✅

Hola {pedido.nombre_cliente},

Tu pedido #{pedido.venta.numero} está listo para entrega.

📍 *Dirección:*
{pedido.direccion_entrega or 'Retiro en local'}

💰 *Total a pagar: ${pedido.venta.total}*

Te esperamos!

🛒 Ferretería Corralón
"""
        return self.enviar_mensaje_texto(pedido.telefono, mensaje)
    
    def enviar_mensaje_pedido_entregado(self, pedido):
        """Enviar mensaje cuando el pedido fue entregado"""
        mensaje = f"""
🚚 *PEDIDO ENTREGADO* 🚚

Hola {pedido.nombre_cliente},

Tu pedido #{pedido.venta.numero} ha sido entregado exitosamente.

💰 *Total pagado: ${pedido.venta.total}*

¡Gracias por confiar en nosotros! 

🛒 Ferretería Corralón
"""
        return self.enviar_mensaje_texto(pedido.telefono, mensaje)
    
    def enviar_mensaje_pedido_cancelado(self, pedido, motivo=''):
        """Enviar mensaje cuando el pedido es cancelado"""
        mensaje = f"""
❌ *PEDIDO CANCELADO* ❌

Hola {pedido.nombre_cliente},

Lamentamos informarte que tu pedido #{pedido.venta.numero} ha sido cancelado.
"""
        if motivo:
            mensaje += f"\n*Motivo:* {motivo}\n"
        
        mensaje += """
Si tienes alguna pregunta, contáctanos.

🛒 Ferretería Corralón
"""
        return self.enviar_mensaje_texto(pedido.telefono, mensaje)
    
    def _normalizar_telefono(self, telefono):
        """Normalizar número de teléfono al formato internacional"""
        # Eliminar caracteres no numéricos
        telefono_limpio = ''.join(c for c in telefono if c.isdigit())
        
        # Si no tiene código de país, agregar +54 (Argentina)
        if not telefono_limpio.startswith('54'):
            telefono_limpio = '54' + telefono_limpio
        
        return '+' + telefono_limpio


def notificar_cambio_estado_pedido(pedido, estado_anterior, estado_nuevo):
    """Función auxiliar para notificar cambios de estado"""
    whatsapp = WhatsAppIntegration()
    
    try:
        if estado_nuevo == 'confirmada' and estado_anterior == 'pendiente':
            return whatsapp.enviar_mensaje_pedido_confirmado(pedido)
        elif estado_nuevo == 'listo' and estado_anterior != 'listo':
            return whatsapp.enviar_mensaje_pedido_listo(pedido)
        elif estado_nuevo == 'entregado' and estado_anterior != 'entregado':
            return whatsapp.enviar_mensaje_pedido_entregado(pedido)
        elif estado_nuevo == 'cancelado' and estado_anterior != 'cancelado':
            return whatsapp.enviar_mensaje_pedido_cancelado(pedido)
    except Exception as e:
        print(f'Error al enviar notificación WhatsApp: {str(e)}')
        return None