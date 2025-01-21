import math

from datetime import time, datetime
from modules.data_providers import api
from modules.service.utils import str_to_date, timezone_correction, log
from modules.data_providers.config_loader import TIME_FILTER, CLOUDINESS_FILTER, TIMEZONE_CORRECTION_AMOUNT

def moon_illumination(illumination_midday: list[float], phase_name: list[str]) -> list:
    """
    Производит расчёт осещенности Луны в полночь, основываясь на данных освещённости в полдень и фазе Луны.

    Args:
        illumination_midday (list[float]): список значений освещенности луны в полдень. Одно значение для каждого дня.
        phase_name (list[str]): список названий фаз луны. Одно значние для каждого дня.
    
    Returns:
        list: Список значений освещенности Луны в полночь для каждого дня.

    Example:
    >>> moon_illumination([15.4, 19.2], ["waxing crescent", "waxing crescent")
    [19.0, 23.1]
    """
    
    waxing = ["new", "waxing crescent", "first quarter", "waxing gibbous"]
    waning = ["full", "waning gibbous", "last quarter", "waning crescent"]
    result = []

    def process_data(noon_percentage: float, phase_name: str) -> float:
        """
        Производит расчёт осещенности Луны в полночь, основываясь на данных освещённости в полдень и фазе Луны.

        Args:
            noon_percentage (float): значение освещенности луны в полдень для одного конкретного дня.
            phase_name (str): Название фазы Луны для одного конкретного дня.
        
        Returns:
            float: значение освещенности Луны в полночь для одного конкретного дня.

        Example:
        >>> process_data(15.4, "waxing crescent")
        19.0
        """

        # Приводим название фазы к нижнему регистру для сравнения
        phase_name = phase_name.lower()

        # Проверяем, является ли название фазы корректным и определяем фазу Луны
        if phase_name in waxing:
            is_waxing = True
        elif phase_name in waning:
            is_waxing = False
        else:
            raise ValueError("Invalid phase name. Please use one of the predefined phase names.")

        # Константы
        T = 29.53          # Синодический месяц (период лунного цикла) в днях
        delta_t = 0.5      # Разница во времени в днях (12 часов)

        # Преобразуем процент освещенности в дробь от 0 до 1
        P_t = noon_percentage / 100.0

        # Убеждаемся, что входной процент находится в допустимых пределах
        if not (0 <= P_t <= 1):
            raise ValueError("Illumination percentage must be between 0 and 100.")

        # Шаг 1: Вычисляем начальный фазовый угол θ в полдень
        cos_theta = 1 - 2 * P_t
        # Убеждаемся, что значение находится в допустимом диапазоне для arccos
        cos_theta = min(max(cos_theta, -1), 1)
        theta = math.acos(cos_theta)

        # Шаг 2: Определяем фазовый угол θ(t) в зависимости от фазы Луны
        if is_waxing:
            theta_t = theta
        else:
            theta_t = 2 * math.pi - theta

        # Шаг 3: Вычисляем изменение фазового угла за Δt
        delta_theta = 2 * math.pi * (delta_t / T)

        # Шаг 4: Вычисляем фазовый угол в полночь
        theta_t_plus_delta = theta_t + delta_theta
        # Нормализуем угол, чтобы он оставался в диапазоне от 0 до 2π
        theta_t_plus_delta = theta_t_plus_delta % (2 * math.pi)

        # Шаг 5: Вычисляем процент освещенности в полночь
        P_t_plus_delta = 0.5 * (1 - math.cos(theta_t_plus_delta))
        illumination_percentage = P_t_plus_delta * 100  # Преобразуем в проценты

        # Добавляем результат в список, применяя поправочный коэффициент 0.98
        result.append(round(illumination_percentage * 0.98, 1))

    for i in range(len(illumination_midday)):
        process_data(illumination_midday[i], phase_name[i])
    
    return result

def is_time_in_range(range_from: time, range_to: time, timestamp_to_check: time) -> bool:
    """
    Проверяет, находится ли заданное время в установленном диапазоне, включая переход через полночь.

    Args:
        range_from (datetime.time): Начальная точка временного диапазона для проверки.
        range_to (datetime.time): Конечная точка временного диапазона для проверки.
        timestamp_to_check (datetime.time): Метка времени, проверяемая на соответствие заданному диапазону.

    Returns:
        bool: Если проверяемая метка времени находится в заданном диапазоне, возвращает True, иначе False.

    Example:
        >>> is_time_in_range(datetime.time(16,0), datetime.time(3,0), datetime.time(19,41))
        True
    """

    # Проверяем, что метка времени попадает под один из критериев: больше или равно начальной точке диапазона ИЛИ больше или равно 00:00 но меньше или равно конечной точке диапазона
    return timestamp_to_check >= range_from or time(0, 0) <= timestamp_to_check <= range_to
    
def filter_cloudiness_data(data: dict, sunset: time) -> dict:
    """
    Фильтрует данные о дате/времени и облачности.

    Фильтрует данные о дате/времени и облачности, оставляя только те записи, которые соответствуют критериям: время - от захода Солнца до $TIME_FILTER, облачность - не более $CLOUDINESS_FILTER.

    Args:
        data (dict): словарь значений время:облачность для 1 конкретного дня
        sunset (datetime.time): информация о времени захода Солнца в этот день. Начальная точка диапазона фильтрации.

    Returns:
        dict: словарь с отфильтрованными значениями date_time и cloudiness
    
    Example:
        >>> filter_data_by_time({datetime.time(22,14) : 15, datetime.time(15,41) : 92}, datetime.time(18,0))
        {datetime.time(22, 14): 15}
    """
    # Создаём копию исходного словаря
    filtered_data = dict(data.items())

    # Перебираем все значения времени и облачности в исходном словаре, и удаляем из
    # копии те пары, которые не попадают в заданный диапазон времени или макисмально
    # допустимный показатель облачности
    for dt, cl in zip(data.keys(), data.values()):
        if not is_time_in_range(sunset, TIME_FILTER, dt) or cl > CLOUDINESS_FILTER:
            del filtered_data[dt]

    return filtered_data

def split_cloudiness_by_days(datetime: dict) -> dict:
    """
    Группирует данные о дате/времени и облачности по дням.

    Разбивает два списка (день+время и облачность), на словарь, 
    который содержит сгруппированные по дням данные об облачности в конкретный час.

    Args:
        datetime (dict): Словарь, содержащий списки date_time (datetime.datetime - полная дата и время) и cloudiness.
    
    Returns:
        dict: Cловарь, содержащий значения времени и облачности, сгруппированные по дням.
    
    Example:
        >>> split_cloudiness_by_days({"date_time":[datetime.datetime(2001,12,6,15,0), datetime.datetime(2001,12,6,16,0)], "cloudiness":[15,25]})
        {datetime.date(2001, 12, 6): {'date_time': {datetime.time(15, 0): 15, datetime.time(16, 0): 25}}}
    """
    grouped_cloudiness = {}
    
    # Перебираем все пары значений дата/время : облачность
    for dt, cl in zip(datetime["date_time"], datetime["cloudiness"]):
    # Если ключ с датой (один конкретный день) для группировки ещё не создана - создаём.
        if dt.date() not in grouped_cloudiness:
            grouped_cloudiness[dt.date()] = {"date_time":{}}
    # Разделям объект datetime.datetime на дату и время, и добавляем их в соответствующий день для группировки.
        grouped_cloudiness[dt.date()]["date_time"][dt.time()] = cl
    
    return grouped_cloudiness

def process_weather_data(clouds_data: dict, moon_data: dict) -> dict:
    """
    Обрабатывает и компонует данные об облачности и луне.

    Обрабатывает и компонует данные об облачности (по часам), фазе и освещенности Луны, времени заката в один единый словарь с группировкой по дням.

    Args:
        clouds_data (dict): содержит данные об облачности, полученные из функции get_clouds_data()
        moon_data (dict): содержит данные о Луне и закате, полученные из функции get_sun_mon_data()

    Returns:
        dict: Итоговый словарь, который содержит в себе обработанные и объединенные данные из обоих словарей.

    Example:
        >>> 1. Группирует clouds_data по дням
        >>> 2. Далее, для каждого из группирующих дней:
            >>> 2.1 Фильтрует данные о времени и облачности, оставляя только те записи, 
                которые попадают в диапазон "от заката до 03:00 ночи (значение по умолчанию.)"
            >>> 2.2 Добавляет запись о времени захода Солнца
            >>> 2.3 Добавляет запись о проценте освещенности Луны в полночь
            >>> 2.4 Добавляем запись о названии фазы Луны
        >>> 3. Возвращает итоговый словарь с разбивкой по дням
    """

    # Названия фаз Луны с переводом
    moon_phase_translation = {
        "new": "Новолуние - \U0001F311",
        "waxing crescent": "Растущий месяц - \U0001F312",
        "first quarter": "Первая четверть - \U0001F313",
        "waxing gibbous": "Растущая Луна - \U0001F314",
        "full": "Полнолуние - \U0001F315",
        "waning gibbous": "Убывающая Луна - \U0001F316",
        "last quarter": "Последняя четверть - \U0001F317",
        "waning crescent": "Убывающий месяц - \U0001F318"
    }

    clouds_data = split_cloudiness_by_days(clouds_data)

    for day, sunset, moon_illumination_data, moon_phase in zip(clouds_data, moon_data["sunset"], moon_data["moon_illumination"], moon_data["moon_phase_name"]):
        clouds_data[day]["date_time"] = filter_cloudiness_data(clouds_data[day]["date_time"], sunset.time())
        clouds_data[day]["sunset"] = sunset.time()
        clouds_data[day]["moon_illumination"] = moon_illumination_data
        clouds_data[day]["moon_phase"] = moon_phase_translation[moon_phase]
    
    # Удаляем последний элемент словаря, т.к. он содержит 00:00 для дня, следующего
    # после последего запрошенного дня. Для этой даты не запрашиваются данные о
    # Луне и Солнце, в следствие чего этот элемент словаря не нужен.
    clouds_data.popitem()

    # Удалим все дни с пустой информацией об облачности (которая была отброшена фильтром)
    # Конструкция list(dict.keys()) итерируется по копии ключей словаря,
    # позволяя изменять словарь, не получая ошибку об изменении длины словаря
    # во время итерации.
    for day in list(clouds_data.keys()):
        if not clouds_data[day]["date_time"]:
            clouds_data.pop(day)

    log(event_type="INFO", message="Данные обработаны.", data=clouds_data)

    return clouds_data

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
    def outdated_data_filter(date_time: list[datetime], cloudiness: list[int]) -> list:
        """
        Фильтрует данные время/облачность, убирая устаревшие данные

        Убирает данные за время, которое уже прошло, относительно момента составления отчёта.
        Происходит параллельная итерация по обоим входным спискам, и если обнаруживается временная метка,
        которая равна или больше текущего момента времени - временная метка переносится в результирующий "очищенный" список,
        а соответствующий показатель облачности для этой метки переносится в аналогичный результирующий список для облачности.

        Args:
            date_time (list[datetime]): Список временных меток
            cloudiness (list[int]): Список показателей облачности в процентах
        
        Returns:
            list: Два списка с отфильтрованными значениями времени и облачности. 
        """
        filtered_date_time = []
        filtered_cloudiness = []

        for dt, cl in zip(date_time, cloudiness):
            if dt.date() == datetime.now().date() and dt.time() <= datetime.now().time():
                pass
            else:
                filtered_date_time.append(dt)
                filtered_cloudiness.append(cl)
        return filtered_date_time, filtered_cloudiness

    data = api.fetch("/clouds-1h", {"windspeed":"kmh", "temperature":"C"})["data_1h"]
    timestamp = data["time"]

    date_time = str_to_date(timestamp, "%Y-%m-%d %H:%M")
    cloudiness = data["totalcloudcover"]

    filtered_date_time, filtered_cloudiness = outdated_data_filter(date_time, cloudiness)

    return {
        "date_time": filtered_date_time,
        "cloudiness": filtered_cloudiness,
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
    data = api.fetch("/sunmoon")["data_day"]

    data["time"] = str_to_date(data["time"], "%Y-%m-%d")
    data["sunset"] = str_to_date(data["sunset"], "%H:%M")
    #Use when API return default timezone sunset instead of the timezone you requested
    #data["sunset"] = timezone_correction(data["sunset"], TIMEZONE_CORRECTION_AMOUNT)

    moon_illumination_percentage = moon_illumination(data["moonilluminatedfraction"], data["moonphasename"])

    return {
        "date": data["time"], 
        "sunset": data["sunset"],
        "moon_illumination": moon_illumination_percentage,
        "moon_phase_name": data["moonphasename"]
        }