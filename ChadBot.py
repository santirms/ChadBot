import requests
import openai
from flask import Flask, request

app = Flask(__name__)

# Credenciales de Tienda Nube
TIENDA_NUBE_STORE_ID = "TU_TIENDA_ID"
TIENDA_NUBE_ACCESS_TOKEN = "TU_ACCESS_TOKEN"
TIENDA_NUBE_API_URL = f"https://api.tiendanube.com/v1/{TIENDA_NUBE_STORE_ID}/products"

# Credenciales de WhatsApp Cloud API
import os

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("mi-token-de-verificación")

# Credenciales de OpenAI GPT-4
OPENAI_API_KEY = "TU_OPENAI_API_KEY"

# Clientes en espera de atención humana
clientes_en_espera = set()

# Función para buscar productos en Tienda Nube
def buscar_producto(nombre_producto):
    headers = {"Authentication": f"Bearer {TIENDA_NUBE_ACCESS_TOKEN}"}
    response = requests.get(TIENDA_NUBE_API_URL, headers=headers)
    productos = response.json()
    
    for producto in productos:
        if nombre_producto.lower() in producto["name"].lower():
            return f"📦 {producto['name']}\n💰 Precio: ${producto['price']}\n📦 Stock: {producto['stock']}\n🔗 {producto['permalink']}"

    return None  # No se encontró el producto

# Función para consultar GPT-4 si la pregunta no es un producto ni una respuesta predefinida
def consultar_gpt(mensaje):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Eres un asistente de ventas de una tienda de tecnología."},
                  {"role": "user", "content": mensaje}]
    )
    return response["choices"][0]["message"]["content"]

# Función para manejar los mensajes
def responder_mensaje(remitente, mensaje):
    global clientes_en_espera

    mensaje = mensaje.lower()  # Convertir mensaje a minúsculas para comparación

    # Diccionario de respuestas personalizadas
    RESPUESTAS = {
        "horarios": "Nuestro horario de atención es de lunes a jueves de 10:30 a 21:00 hs, viernes y sábados de 10:30 a 22:00 hs.",
        "hola": "Hola! ¿Cómo estas? Gracias por comunicarte con Igeneration Tech Store ¿En que te puedo ayudar?",
        "medios de pago": "Aceptamos pagos con transferencia bancaria con un -10% de descuento, MercadoPago, MODO, tarjetas de debito y credito con hasta 6 cuotas sin interés en todo el sitio!",
        "tarjetas": "Si! Aceptamos todas las tarjetas de credito, podes pagar en hasta 6 cuotas sin interés",
        "local": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "ubicacion": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "ubicados" : "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "ubicación": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "retirar": "Sí, podes retirar tu compra por nuestro local en el Boulevard Shopping, Adrogué. Te avisaremos en cuanto esté lista.",
        "envíos": "Sí, realizamos envíos a todo el país por Correo Argentino o Andreani. Para CABA y GBA tenemos envío gratis con nuestra logística.",
        "consola retro": "Tenemos varias en stock, se diferencian en la cantidad de juegos y consolas que emulan, te recomiendo la X2 Plus, es la más completa, pero todas estan buenisimas para recordar los juegos clasicos! Te dejo el link https://igeneration.com.ar/consolas/?mpage=2",
        "game stick": "Sí, tenemos stock. La más completa es el modelo X2 Plus, con mayor variedad de juegos de PS1, PSP y Nintendo 64. Podes ver las opciones en el siguiente enlace: https://igeneration.com.ar/consolas/?mpage=2",
        "productos": "Tenemos una gran variedad de productos de tecnología y realidad virtual. ¿Buscas algo en particular?",
        "tv box": "Tenemos varios modelos con Android oficial para usar aplicaciones como Netflix, Prime, Max con suscripción. También tenemos genéricos con acceso a series y películas. Te dejo el link para que los puedas ver: https://igeneration.com.ar/media-streaming/?mpage=2",
        "garantía": "Todos nuestros productos tienen garantía de 6 o 12 meses por fallas de fábrica.",
        "conversor": "Tenemos varios modelos con Android oficial para usar aplicaciones como Netflix, Prime, Max con suscripción. También tenemos genéricos con acceso a series y películas. Te dejo el link para que los puedas ver: https://igeneration.com.ar/media-streaming/?mpage=2",
        "cuotas": "Sí, podes pagar con tarjeta en hasta 6 cuotas sin interés.",
        "gracias": "Gracias a vos! Espero haberte ayudado con la consulta",
        "auriculares": "Si, te paso el link con los modelos disponibles https://igeneration.com.ar/audio/auriculares/?mpage=3",
        "teclados": "Si, te paso el link con los modelos disponibles https://igeneration.com.ar/perifericos/teclados/",
        "mouse": "Si, te paso el link con los modelos disponibles https://igeneration.com.ar/perifericos/mouses/",
        "cbu": "Te paso los datos para realizar la transferencia por tu pedido. Alias: igeneration.galicia - CUIT 30717295362 - Titular: Igeneration SRL."
    }

    # Si el cliente pide atención humana
    if mensaje in ["humano", "quiero hablar con alguien", "necesito ayuda"]:
        clientes_en_espera.add(remitente)
        return "🧑‍💼 Hace click en el enlace https://wa.me/5491153876227 y te pondremos en contacto con un asesor comercial en breve."

    # Si el cliente está en espera de atención humana, no responde automáticamente
    if remitente in clientes_en_espera:
        return None

    # Buscar si el mensaje coincide con alguna pregunta frecuente
    for clave, respuesta in RESPUESTAS.items():
        if clave in mensaje:
            return respuesta

    # Respuesta por defecto si no coincide con ninguna pregunta
    return "No entendí tu consulta. ¿Podrías reformularla o darme más detalles?"

    # Temporalmente, desactivamos Tienda Nube si no está configurada
    if "TIENDA_NUBE_ACCESS_TOKEN" not in globals() or not TIENDA_NUBE_ACCESS_TOKEN:
        print("⚠ Tienda Nube no está configurada. Respondiendo con mensaje por defecto.")
        return "🤖 Lo siento, la consulta sobre productos aún no está disponible."

    # Temporalmente, desactivamos GPT-4 si no está configurado
    if "OPENAI_API_KEY" not in globals() or not OPENAI_API_KEY:
        print("⚠ GPT-4 no está configurado. Respondiendo con mensaje por defecto.")
        return "🤖 Lo siento, aún no puedo responder preguntas generales."

    # Si ya tienes Tienda Nube configurado, puedes activar esta línea más adelante:
    # respuesta_producto = buscar_producto(mensaje)
    # if respuesta_producto:
    #     return respuesta_producto

    # Si ya tienes GPT-4 configurado, puedes activar esta línea más adelante:
    # return consultar_gpt(mensaje)

    return "🤖 No entendí tu consulta. ¿Puedes reformularla?"

# Webhook de WhatsApp
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "mi-token-de-verificación"

import sys

import requests

@app.route("/webhook", methods=["POST"])
def webhook():
    print("📩 Se recibió un POST en /webhook")
    sys.stdout.flush()

    try:
        raw_data = request.data
        json_data = request.get_json(silent=True)

        print(f"📩 JSON recibido: {json_data}")
        sys.stdout.flush()

        if "messages" in json_data["entry"][0]["changes"][0]["value"]:
            mensaje = json_data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
            remitente = json_data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
            
            print(f"📩 Mensaje recibido: {mensaje} de {remitente}")
            sys.stdout.flush()

            # Llamar a la función correcta (antes llamaba a procesar_mensaje)
            respuesta = responder_mensaje(remitente, mensaje)

            # Si la respuesta no es None, enviarla
            if respuesta:
                enviar_respuesta(remitente, respuesta)

        return "OK", 200

    except Exception as e:
        print(f"❌ Error al procesar la solicitud: {str(e)}")
        sys.stdout.flush()
        return "Error", 500

    except Exception as e:
        print(f"❌ Error al procesar la solicitud: {str(e)}")
        sys.stdout.flush()
        return "Error", 500

    except Exception as e:
        print(f"❌ Error al procesar la solicitud: {str(e)}")
        sys.stdout.flush()
        return "Error", 500


# Función para enviar mensajes de WhatsApp

import time

def enviar_respuesta(numero, mensaje):
    time.sleep(2)  # Agrega una pausa de 2 segundos antes de responder

    url = "https://graph.facebook.com/v18.0/602432446282342/messages"
    headers = {
        "Authorization": f"Bearer EAAHz1wFDZCQABOxZCWHVRs0XdkSrCaKLbvHyS2ABw3tnnZBtgG4fLE4houMZBUiaxMiXUoLsvCOyycuXiSmAMM32Wk2auVWXJikqOAwhOSjdT4ZChdYUYabKzic9aLjk2JV12vmUfw9MEsqwwF3hYzswZCnEsKwwKZChbDxjbgmkRB1zThymTxK3WH4XcmrUZBEGgOGtzAZDZD",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }

    response = requests.post(url, headers=headers, json=data)

    print(f"✅ Respuesta enviada a {numero}: {mensaje}")
    print(f"📩 Respuesta API: {response.json()}")
    sys.stdout.flush()


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Usa el puerto asignado por Render
    app.run(host="0.0.0.0", port=port)  # Escucha en todas las interfaces

