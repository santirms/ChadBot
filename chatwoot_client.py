import requests
import os

# Config desde variables de entorno
CHATWOOT_URL = os.environ.get("CHATWOOT_URL")  # Ej: https://chat.igeneration.com.ar
API_KEY = os.environ.get("CHATWOOT_API_KEY")
INBOX_ID = os.environ.get("CHATWOOT_INBOX_ID")  # ID del inbox (WhatsApp)
ACCOUNT_ID = 2  # Normalmente 1 si no cambiaste la cuenta principal

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def obtener_o_crear_conversacion(phone_number):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations"
    payload = {
        "source_id": phone_number,
        "inbox_id": int(INBOX_ID),
        "contact": {
            "name": f"Cliente {phone_number}",
            "phone_number": phone_number
        }
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code in [200, 201]:
        conversation_id = response.json()["id"]
        print(f"✅ Conversación Chatwoot ID {conversation_id} obtenida/creada para {phone_number}")
        return conversation_id
    else:
        print(f"❌ Error al obtener/crear conversación: {response.status_code} {response.text}")
        return None

def enviar_mensaje(conversation_id, mensaje):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    payload = {
        "content": mensaje,
        "message_type": "outgoing"
    }
    
    print(f"📡 Enviando mensaje a Chatwoot:")
    print(f"URL: {url}")
    print(f"Headers: {HEADERS}")
    print(f"Payload: {payload}")
      
    response = requests.post(url, json=payload, headers=HEADERS)

    if response.ok:
        print("✅ Mensaje enviado a Chatwoot")
    else:
        print(f"❌ Error enviando mensaje: {response.status_code} {response.text}")
