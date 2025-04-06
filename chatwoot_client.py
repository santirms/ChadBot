import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
CHATWOOT_URL = os.environ.get("CHATWOOT_URL")
CHATWOOT_EMAIL = os.environ.get("CHATWOOT_EMAIL")
CHATWOOT_PASSWORD = os.environ.get("CHATWOOT_PASSWORD")
INBOX_ID = os.environ.get("CHATWOOT_INBOX_ID")
ACCOUNT_ID = os.environ.get("CHATWOOT_ACCOUNT_ID")

def obtener_token_temporal():
    login_url = f"{CHATWOOT_URL}/auth/sign_in"
    payload = {
        "email": CHATWOOT_EMAIL,
        "password": CHATWOOT_PASSWORD
    try:
        response = requests.post(login_url, json=payload)
        print(f"🔁 Respuesta completa del login: {response.status_code} {response.text}")  # NUEVA LÍNEA 👈

        if response.status_code == 200:
            print("🔑 Login exitoso en Chatwoot")
            return response.json().get("data", {}).get("access_token")
        else:
            print(f"❌ Error al iniciar sesión: {response.status_code} {response.text}")
            return None
    }

    try:
        response = requests.post(login_url, json=payload)
        if response.status_code == 200:
            token = response.headers.get("api-access-token")
            print(f"🔑 Login exitoso en Chatwoot. Token: {token}")
            return token

        else:
            print(f"❌ Error al iniciar sesión: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de red al intentar login: {str(e)}")
        return None

def obtener_o_crear_conversacion(phone_number):
    token = obtener_token_temporal()
    if not token:
        return None

    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": token
    }

    payload = {
        "source_id": phone_number,
        "inbox_id": int(INBOX_ID),
        "contact": {
            "name": f"Cliente {phone_number}",
            "phone_number": phone_number
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        conversation_id = response.json()["id"]
        print(f"✅ Conversación Chatwoot ID {conversation_id} obtenida/creada para {phone_number}")
        return conversation_id
    else:
        print(f"❌ Error al obtener/crear conversación: {response.status_code} {response.text}")
        return None

def enviar_mensaje(conversation_id, mensaje):
    token = obtener_token_temporal()
    if not token:
        return

    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "api_access_token": token
    }

    payload = {
        "content": mensaje,
        "message_type": "outgoing"
    }

    print(f"📡 Enviando mensaje a Chatwoot:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {payload}")

    response = requests.post(url, json=payload, headers=headers)

    if response.ok:
        print("✅ Mensaje enviado a Chatwoot")
    else:
        print(f"❌ Error enviando mensaje: {response.status_code} {response.text}")

