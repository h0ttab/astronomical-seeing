from modules.data_providers.config_loader import BOT_TOKEN, CHAT_ID
import requests

def bot_send_message(message: str) -> bool:
    """
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
    response = requests.get(url, payload)
    return response.json()["ok"]