from modules.data_providers.config_loader import BOT_TOKEN, CHAT_ID
import requests


def bot_send_message(message: str) -> bool:
    """
    Sends a message via Telegram bot

    Args:
        message (str): Text message to send.

    Returns:
        bool: Message sending status received from the Telegram API response

    Examples:
        >>> bot_send_message("Hello, friend!")
            True
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        if response.json().get("ok"):
            return True
        else:
            raise requests.RequestException(response.text)
    except requests.RequestException as error:
        raise requests.RequestException(f"An error occurred while sending a message to Telegram: {error}")