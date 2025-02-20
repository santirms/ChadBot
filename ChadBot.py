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
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

# Credenciales de OpenAI GPT-4
OPENAI_API_KEY = "TU_OPENAI_API_KEY"

# Clientes en espera de atención humana
clientes_en_espera = set()

# Respuestas predefinidas
RESPUESTAS_PREDEFINIDAS = {
    "envíos": "📦 Realizamos envíos a todo el país en 24-48 hs.",
    "formas de pago": "💳 Aceptamos tarjetas, transferencia y MercadoPago.",
    "horarios": "🕒 Nuestro horario de atención es de 9 a 18 hs.",
    "garantía": "🛠 Todos nuestros productos tienen garantía de 6 meses."
}

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

    # Si el cliente pide atención humana
    if mensaje.lower() in ["humano", "quiero hablar con alguien", "necesito ayuda"]:
        clientes_en_espera.add(remitente)
        return "🧑‍💼 Te pondremos en contacto con un asesor en breve."

    # Si el cliente está en espera de atención humana, no responde automáticamente
    if remitente in clientes_en_espera:
        return None  

    # Buscar si es una consulta predefinida
    for clave, respuesta in RESPUESTAS_PREDEFINIDAS.items():
        if clave in mensaje.lower():
            return respuesta

    # Si no es consulta predefinida, buscar en Tienda Nube
    respuesta_producto = buscar_producto(mensaje)
    if respuesta_producto:
        return respuesta_producto

    # Si no se encuentra nada, consulta GPT-4
    return consultar_gpt(mensaje)

# Webhook de WhatsApp
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge") if request.args.get("hub.verify_token") == VERIFY_TOKEN else "Error"

    data = request.json
    if data.get("entry"):
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        remitente = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        
        respuesta = responder_mensaje(remitente, mensaje)
        if respuesta:
            enviar_mensaje(remitente, respuesta)

    return "OK"

# Función para enviar mensajes de WhatsApp
def enviar_mensaje(destinatario, mensaje):
    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {"body": mensaje},
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    app.run(port=5000)
