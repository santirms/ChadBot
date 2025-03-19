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

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ Webhook verificado correctamente.")
            return challenge, 200
        else:
            print("❌ Fallo en la verificación del Webhook.")
            return "Error de verificación", 403

    if request.method == "POST":
        print("📩 Se recibió un POST en /webhook")
        
        try:
            raw_data = request.data  # Obtener datos en crudo
            json_data = request.get_json(silent=True)  # Intentar convertir a JSON

            print(f"📩 Datos crudos recibidos: {raw_data}")  # Mostrar cualquier dato recibido
            if json_data:
                print(f"📩 Datos en JSON: {json_data}")  # Ver el JSON estructurado
            else:
                print("⚠ No se recibió JSON válido en el POST.")

            return "OK", 200
        except Exception as e:
            print(f"❌ Error al procesar la solicitud: {str(e)}")
            return "Error", 500

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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto asignado por Render
    app.run(host="0.0.0.0", port=10000)  # Escucha en todas las interfaces

