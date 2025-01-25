from modules.service.utils import log
from modules.data_processing.weather import moon_illumination
from modules.data_providers.config_loader import FORECAST_DAYS, API_KEY, TIMEZONE, LATITUDE, LONGITUDE

from datetime import datetime

import requests
from requests.exceptions import RequestException

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
    params = add_params | REQUEST_COMMON_PARAMS
    log(event_type="INFO", message=f"Отправка GET запроса на адрес {url}", data=f"Параметры запроса:\n{params}")
    try:
        data = requests.get(url, params).json()
        log(event_type="INFO", message="Получен ответ от API.", data=data)
        return data
    except RequestException as exception:
        log(event_type="ERROR", message=f"При запросе к API возникла ошибка: {exception}")
        raise exception

def get_clouds_data() -> dict:
    """
    Запрашивает через API данные об облачности.
    Запрашивает данные об облачности, а также парсит данные о дате и времени, 
    и из строки (str) приводит их к типу данных datetime.

    Returns:
        dict: Словарь, который содержит в себе две пары ключ:значение - date_time и cloudiness, 
            которые содержат в себе почасовые данные об облачности для всего запрошенного периода. 
            Каждая запись в списке даты и времени относится к идентичной ей по порядку записи из 
            списка с показателями облачности.

    Example:
    >>> get_clouds_data()
        {'date_time': [datetime.datetime(2025, 1, 9, 0, 0), datetime.datetime(2025, 1, 9, 1, 0)], 'cloudiness': [65, 32]}
    """

    data = fetch("/clouds-1h", {"windspeed":"kmh", "temperature":"C"})["data_1h"]

    date_time = [datetime.strptime(timestamp, "%Y-%m-%d %H:%M") for timestamp in data["time"]]
    cloudiness = data["totalcloudcover"]

    return {
        "date_time": date_time,
        "cloudiness": cloudiness,
        }

def get_sun_moon_data() -> dict:
    """
    Запрашивает по API данные о заходе/восходе Солнца и Луны, вычисляет освещенность Луны в процентах.
    Запрашивает подневной прогноз данных о Солнце и Луне, а также (при необходимости) корректирует время о заходе Солнца согласно заданному часовому поясу. Вычисляет освещенность Луны в процентах на время полуночи в конце каждого дня.

    Returns:
        dict: Словарь, содержащий 4 набора данных - date, sunset, moon_illumination, moon_phase_name. Каждому элементу списка соответствует элемент из других списком с тем же индексом.

    Example:
        >>> get_sun_moon_data()
            {'date': [datetime.datetime(2025, 1, 9, 0, 0)], 'sunset': [datetime.datetime(1900, 1, 1, 16, 20)],'moon_illumination': [79.8], 'moon_phase_name': ['waxing gibbous']}
    """
    data = fetch("/sunmoon")["data_day"]

    data["time"] = [datetime.strptime(timestamp, "%Y-%m-%d") for timestamp in data["time"]]
    data["sunset"] = [datetime.strptime(timestamp, "%H:%M") for timestamp in data["sunset"]]
    #Use when API return default timezone sunset instead of the timezone you requested
    #data["sunset"] = timezone_correction(data["sunset"], TIMEZONE_CORRECTION_AMOUNT)

    moon_illumination_percentage = moon_illumination(data["moonilluminatedfraction"], data["moonphasename"])

    return {
        "date": data["time"], 
        "sunset": data["sunset"],
        "moon_illumination": moon_illumination_percentage,
        "moon_phase_name": data["moonphasename"]
        }