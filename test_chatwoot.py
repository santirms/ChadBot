import os
import requests

CHATWOOT_URL = os.environ.get("CHATWOOT_URL")  # Ej: https://chat.igeneration.com.ar
API_KEY = os.environ.get("CHATWOOT_API_KEY")
print("🔎 Token real:", repr(API_KEY))
print(f"🔐 TOKEN RAW: {repr(API_KEY)}")

if not CHATWOOT_URL or not API_KEY:
    print("❌ Faltan variables de entorno: CHATWOOT_URL o CHATWOOT_API_KEY")
    exit(1)

print(f"🔑 TOKEN USADO: {API_KEY}")
print(f"🌍 URL USADA: {CHATWOOT_URL}")

url = f"{CHATWOOT_URL}/api/v1/profile"
headers = {
    "Content-Type": "application/json",
    "api_access_token": API_KEY
}

try:
    response = requests.get(url, headers=headers)
    if response.ok:
        print("✅ ¡Conexión exitosa con Chatwoot!")
        print("👤 Perfil:", response.json())
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
