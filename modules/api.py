from modules.utils import merge_dicts
from modules.config_loader import FORECAST_DAYS, API_KEY, TIMEZONE, LATITUDE, LONGITUDE

import requests

#Базовый URL для API сервиса погоды
API_BASE_URL = "http://my.meteoblue.com/packages/"

#Базовые (обязательные) параметры GET запроса, которые отправляются при каждом запросе к API.
REQUEST_COMMON_PARAMS = {
    "apikey" : API_KEY,
    "tz" : TIMEZONE,
    "forecast_days" : FORECAST_DAYS,
    "format" : "json",
    "lat" : LATITUDE,
    "lon" : LONGITUDE,
}

def fetch(endpoint: str, add_params: dict = {}) -> dict:
    """
    Отправляет GET запрос к API и принимает данные.
    
    Запрашивает (GET) и принимает данные от API сервиса. Возвращает JSON-объект (словарь) с данными ответа от API.

    Args:
        endpoint (str): Конкретный эндпоинт API-сервиса, который подставляется в конец базового URL, 
            заданного в качестве глобальной переменной API_BASE_URL
        add_params (dict, optional): Дополнительный набор параметров GET запроса к сервису API. 
            Добавляются к базовым параметрам, заданным в глобальной переменной REQUEST_COMMON_PARAMS.

    Returns:
        dict: Возвращает полученные данные в виде словаря (из JSON)

    Example:
        >>> fetch("/api_service", {"city":"Moscow})
        {"response_code":200, "requested_city:"Moscow", "current_time":"21:30"}
    """

    url = API_BASE_URL + endpoint.lstrip(" /")
    params = merge_dicts(add_params, REQUEST_COMMON_PARAMS)
    data = requests.get(url, params).json()

    return data