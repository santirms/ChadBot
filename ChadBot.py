import os
from dotenv import load_dotenv
import requests
import time
import sys
from flask import Flask, request

load_dotenv()

print("🔎 Variables de entorno disponibles:")
for key, value in os.environ.items():
    if "CHATWOOT" in key:
        print(f"{key} = {value}")
        
print("🔒 VERIFY_TOKEN =", repr(os.environ.get("VERIFY_TOKEN")))

app = Flask(__name__)

# Credenciales de Tienda Nube
TIENDA_NUBE_STORE_ID = "TU_TIENDA_ID"
TIENDA_NUBE_ACCESS_TOKEN = "TU_ACCESS_TOKEN"
TIENDA_NUBE_API_URL = f"https://api.tiendanube.com/v1/{TIENDA_NUBE_STORE_ID}/products"

# Credenciales de WhatsApp Cloud API
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.environ.get("mi-token-de-verificación")

# Clientes en espera de atención humana
clientes_en_espera = set()
intentos_fallidos = {}

# Función para buscar productos en Tienda Nube
def buscar_producto(nombre_producto):
    headers = {"Authentication": f"Bearer {TIENDA_NUBE_ACCESS_TOKEN}"}
    response = requests.get(TIENDA_NUBE_API_URL, headers=headers)
    productos = response.json()

    for producto in productos:
        if nombre_producto.lower() in producto["name"].lower():
            return f"📦 {producto['name']}\n💰 Precio: ${producto['price']}\n📦 Stock: {producto['stock']}\n🔗 {producto['permalink']}"

    return None

# Función para manejar los mensajes
def responder_mensaje(remitente, mensaje):
    global clientes_en_espera, intentos_fallidos

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
        "drones": "Si! los drones que tenemos en stock son de principiante, te paso el link https://igeneration.com.ar/gadgets/drones/",
        "dron": "Si! los drones que tenemos en stock son de principiante, te paso el link https://igeneration.com.ar/gadgets/drones/",
        "teclados": "Si, te paso el link con los modelos disponibles https://igeneration.com.ar/perifericos/teclados/",
        "mouse": "Si, te paso el link con los modelos disponibles https://igeneration.com.ar/perifericos/mouses/",
        "cbu": "Te paso los datos para realizar la transferencia por tu pedido. Alias: igeneration.galicia - CUIT 30717295362 - Titular: Igeneration SRL."
    }

    if mensaje in ["humano", "quiero hablar con alguien", "necesito ayuda"]:
        clientes_en_espera.add(remitente)
        return "🧑‍💼 Hace click en el enlace https://wa.me/5491153876227 y te pondremos en contacto con un asesor comercial en breve."

    if remitente in clientes_en_espera:
        if mensaje in ["sí", "si", "dale", "ok", "quiero", "quiero hablar"]:
            return "🧑‍💼 Hace click en el enlace https://wa.me/5491153876227 y te pondremos en contacto con un asesor comercial en breve."
        return None

    for clave, respuesta in RESPUESTAS.items():
        if clave in mensaje:
            if remitente in intentos_fallidos:
                del intentos_fallidos[remitente]
            return respuesta

    intentos_fallidos[remitente] = intentos_fallidos.get(remitente, 0) + 1

    if intentos_fallidos[remitente] >= 3:
        intentos_fallidos[remitente] = 0
        return "🤖 No encontré una respuesta automática. ¿Querés que te contacte un asesor humano? Responé *humano* para derivarte."

    return "No entendí tu consulta. ¿Podrías reformularla o preguntarme algo distinto?"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificación de webhook desde Meta
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verificado correctamente con Meta.")
            return challenge, 200
        else:
            print("❌ Falló la verificación del webhook con Meta.")
            return "Error de verificación", 403

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

                # 🔁 Enviar también a Chatwoot
                from chatwoot_client import obtener_o_crear_conversacion, enviar_mensaje
                conversation_id = obtener_o_crear_conversacion(remitente)
                if conversation_id:
                    enviar_mensaje(conversation_id, respuesta)

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
    
@app.route("/test_chatwoot", methods=["GET"])
def test_chatwoot():
    CHATWOOT_URL = os.environ.get("CHATWOOT_URL")
    API_KEY = os.environ.get("CHATWOOT_API_KEY")

    if not CHATWOOT_URL or not API_KEY:
        return "❌ Faltan variables de entorno", 500

    url = f"{CHATWOOT_URL}/api/v1/profile"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.ok:
            return f"✅ ¡Conexión exitosa! Perfil: {response.json()}"
        else:
            return f"❌ Error {response.status_code}: {response.text}", response.status_code
    except Exception as e:
        return f"❌ Excepción: {str(e)}", 500
        
@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("📩 GET recibido para verificación")
    print(f"Modo: {mode}, Token: {token}, Challenge: {challenge}")
    sys.stdout.flush()

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "❌ Verificación fallida", 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

