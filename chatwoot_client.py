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
    }

    try:
        response = requests.post(login_url, json=payload)
        print(f"🔁 Respuesta completa del login: {response.status_code} {response.text}")

        if response.status_code == 200:
            token = response.headers.get("access-token")  # ✅ CORREGIDO
            uid = response.headers.get("uid")
            client = response.headers.get("client")

            print(f"🔑 Login exitoso en Chatwoot. Token: {token}")
            return {
                "access-token": token,
                "uid": uid,
                "client": client
            }
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

    headers = {
        "Content-Type": "application/json",
        **token
    }

    # 1. Buscar o crear el contacto
    contact_url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/contacts"
    contact_payload = {
        "name": f"Cliente {phone_number}",
        "phone_number": phone_number,
        "identifier": phone_number
    }

    try:
        response = requests.post(contact_url, json=contact_payload, headers=headers)
        if response.status_code in [200, 201]:
            contact_id = response.json()["id"]
            print(f"✅ Contacto creado/encontrado: {contact_id}")
        else:
            print(f"❌ Error creando contacto: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción al crear contacto: {e}")
        return None

    # 2. Crear conversación con el contact_id
    conv_url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations"
    conv_payload = {
        "inbox_id": int(INBOX_ID),
        "contact_id": contact_id
    }

    try:
        response = requests.post(conv_url, json=conv_payload, headers=headers)
        if response.status_code in [200, 201]:
            conversation_id = response.json()["id"]
            print(f"✅ Conversación creada: {conversation_id}")
            return conversation_id
        else:
            print(f"❌ Error creando conversación: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción al crear conversación: {e}")
        return None

def enviar_mensaje(conversation_id, mensaje):
    token = obtener_token_temporal()
    if not token:
        return

    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    headers = {
        "Content-Type": "application/json",
        "access-token": token["access-token"],
        "uid": token["uid"],
        "client": token["client"]
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


