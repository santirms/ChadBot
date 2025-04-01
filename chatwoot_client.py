import requests

CHATWOOT_URL = "https://chat.igeneration.com.ar"
API_KEY = "0a2963a3ace6c3871152c88ee2a436fb3ee1e039"
ACCOUNT_ID = 1  # cambiar si tenés más de una cuenta

def send_to_chatwoot(conversation_id, message):
    url = f"{CHATWOOT_URL}/api/v1/accounts/{ACCOUNT_ID}/conversations/{conversation_id}/messages"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "content": message
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print("✅ Mensaje enviado a Chatwoot")
    except requests.exceptions.RequestException as e:
        print("❌ Error al enviar a Chatwoot:", e)
