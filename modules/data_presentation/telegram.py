from modules.data_providers.config_loader import BOT_TOKEN, CHAT_ID
from modules.service.utils import log
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
    try:
        response = requests.get(url, payload)
        # Если Telegram API ответил статусом "ok": True, возвращаем True
        if response.json()["ok"]:
            return True
        # Иначе, вызываем ошибку
        else:
            raise requests.RequestException(response.json())
    # В случае иной ошибки (например, ошибка соединения) - вызываем ошибку
    except requests.RequestException as error:
        log(event_type="ERROR", message=f"При отправке сообщения в Telegram произошла ошибка: {error}")
        raise requests.RequestException(f"При отправке сообщения в Telegram произошла ошибка: {error}")