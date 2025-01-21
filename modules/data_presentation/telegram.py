from modules.data_providers.config_loader import BOT_TOKEN, CHAT_ID
import requests

def bot_send_message(message: str) -> bool:
    """
    Отправляет сообщение через Telegram бот

    Args:
        message (str): Текстовое сообщение для отправки.

    Returns:
        bool: Статус отправки сообщения, полученный в ответ от Telegram API
    
    Examples:
        >>> bot_send_message("Hello, friend!")
            True
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
            "chat_id": CHAT_ID,
            "text": message
        }
    response = requests.get(url, payload)

    return response.json()["ok"]