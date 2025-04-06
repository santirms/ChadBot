import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Variables de entorno
CHATWOOT_URL = os.environ.get("CHATWOOT_URL")  # Ej: https://chat.igeneration.com.ar
EMAIL = os.environ.get("CHATWOOT_EMAIL")
PASSWORD = os.environ.get("CHATWOOT_PASSWORD")
INBOX_ID = os.environ.get("CHATWOOT_INBOX_ID")
ACCOUNT_ID = os.environ.get("CHATWOOT_ACCOUNT_ID")

# 🔐 Autenticación con email/contraseña
def obtener_headers_autenticacion():
    login_url = f"{CHATWOOT_URL}/auth/sign_in"
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }

    response = requests.post(login_url, json=login_data)
    if response.status_code == 200:
        print("✅ Login exitoso en Chatwoot")
        return {
            "Content-Type": "application/json",
            "access-token": response.headers["access-token"],
            "client": response.headers["client"],
            "uid": response.headers["uid"]
        }
    else:
        print(f"❌ Error al loguearse en Chatwoot: {response.status_code} {response.text}")
        return None

# Crear u obtener conversación
def obtener_o_crear_conversacion(phone_number):
    headers = obtener_headers_autenticacion()
    if not headers:
        return None

    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations"
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

# Enviar mensaje a conversación
def enviar_mensaje(conversation_id, mensaje):
    headers = obtener_headers_autenticacion()
    if not headers:
        return

    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
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
