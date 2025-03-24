import requests
import openai
import os
import time
import sys
from flask import Flask, request

app = Flask(__name__)

# Credenciales de Tienda Nube
TIENDA_NUBE_STORE_ID = "TU_TIENDA_ID"
TIENDA_NUBE_ACCESS_TOKEN = "TU_ACCESS_TOKEN"
TIENDA_NUBE_API_URL = f"https://api.tiendanube.com/v1/{TIENDA_NUBE_STORE_ID}/products"

# Credenciales de WhatsApp Cloud API
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("mi-token-de-verificación")

# Credenciales de OpenAI GPT-4
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Inicializar cliente OpenAI con nueva interfaz (openai>=1.0.0)
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

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

# Función para manejar los mensajes
def responder_mensaje(remitente, mensaje):
    global clientes_en_espera

    mensaje = mensaje.lower()

    RESPUESTAS = {
        "horarios": "Nuestro horario de atención es de lunes a jueves de 10:30 a 21:00 hs, viernes y sábados de 10:30 a 22:00 hs.",
        "hola": "Hola! ¿Cómo estas? Gracias por comunicarte con Igeneration Tech Store ¿En que te puedo ayudar?",
        "medios de pago": "Aceptamos pagos con transferencia bancaria con un -10% de descuento, MercadoPago, MODO, tarjetas de debito y credito con hasta 6 cuotas sin interés en todo el sitio!",
        "tarjetas": "Si! Aceptamos todas las tarjetas de credito, podes pagar en hasta 6 cuotas sin interés",
        "local": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "ubicacion": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "ubicados": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "ubicación": "Estamos en Av. Hipolito Yrigoyen 13.298 Boulevard Shopping 1° Piso Local 252, Adrogué, Buenos Aires. ¡Te esperamos!",
        "retirar": "Sí, podes retirar tu compra por nuestro local en el Boulevard Shopping, Adrogué. Te avisaremos en cuanto esté lista.",
        "envíos": "Sí, realizamos envíos a todo el país por Correo Argentino o Andreani. Para CABA y GBA tenemos envío gratis con nuestra logística.",
        "envios": "Sí, realizamos envíos a todo el país por Correo Argentino o Andreani. Para CABA y GBA tenemos envío gratis con nuestra logística.",
        "consola retro": "Tenemos varias en stock, se diferencian en la cantidad de juegos y consolas que emulan, te recomiendo la X2 Plus, es la más completa, pero todas estan buenisimas para recordar los juegos clasicos! Te dejo el link https://igeneration.com.ar/consolas/?mpage=2",
        "consolas retro": "Tenemos varias en stock, se diferencian en la cantidad de juegos y consolas que emulan, te recomiendo la X2 Plus, es la más completa, pero todas estan buenisimas para recordar los juegos clasicos! Te dejo el link https://igeneration.com.ar/consolas/?mpage=2",
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

    if mensaje in ["humano", "quiero hablar con alguien", "necesito ayuda"]:
        clientes_en_espera.add(remitente)
        return "🧑‍💼 Hace click en el enlace https://wa.me/5491153876227 y te pondremos en contacto con un asesor comercial en breve."

    if remitente in clientes_en_espera:
        return None

    for clave, respuesta in RESPUESTAS.items():
        if clave in mensaje:
            return respuesta

    try:
        respuesta_gpt = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sos un asistente de atención al cliente de iGeneration. Respondé de forma clara y amable."},
                {"role": "user", "content": mensaje}
            ],
            max_tokens=150
        )
        return respuesta_gpt.choices[0].message.content

    except Exception as e:
        print(f"❌ Error al llamar a GPT: {e}")
        return "Disculpá, no pude entender tu consulta. ¿Podés reformularla?"

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

            respuesta = responder_mensaje(remitente, mensaje)

            if respuesta:
                enviar_respuesta(remitente, respuesta)

        return "OK", 200

    except Exception as e:
        print(f"❌ Error al procesar la solicitud: {str(e)}")
        sys.stdout.flush()
        return "Error", 500

def enviar_respuesta(numero, mensaje):
    time.sleep(2)

    url = "https://graph.facebook.com/v18.0/602432446282342/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
