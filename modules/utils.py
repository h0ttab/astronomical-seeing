from datetime import datetime, timedelta
from modules.config_loader import CLOUDINESS_FILTER

today_date = str(datetime.now().date())

def merge_dicts(*dicts: dict) -> dict:
    """
    Производит конкатенацию (слияние) словарей. Если передан только один словарь, возвращает его в исходном виде.

    Args:
        *dicts (dict): Словари для последующего слияния, переданные как набор аргументов.
    
    Returns:
        dict: Cловарь, являющийся результатом слияния всех переданных в функцию словарей.
    
    Example:
        >>> merge_dicts({"name":"Vasya", "age":22}, {"last_name":"Ivanov})
        {"name":"Vasya", "age":22, "last_name":"Ivanov"}
    """
    merge_result = []

    # Проходимся по каждому словарю, и прибавляем к общему результату список (list)
    # из пар ключ-значение этого словаря.
    for dictionary in dicts:
        merge_result += list(dictionary.items())

    # Преобразуем набор "слепленных" вместе списков в словарь.
    merge_result = dict(merge_result)

    return merge_result

def str_to_date(timestamps: list[str], timestamp_format:str) -> list[datetime]:
    """
    Преобразует список строк с датой и временем в объекты datetime.

    Args:
        timestamps (list[str]): Список строковых представлений даты и времени.
        timestamp_format (str): Шаблон для парсинга строки в объект datetime.
            Пример: "%Y-%m-%d %H:%M:%S".

    Returns:
        list[datetime]: Список объектов datetime, преобразованных из строк.

    Example:
        >>> str_to_date(["2024-05-15 15:21:10", "2022-01-05 15:14:13"], "%Y-%m-%d %H:%M:%S")
        [datetime.datetime(2024, 5, 15, 15, 21, 10), datetime.datetime(2022, 1, 5, 15, 14, 13)]
    """
    formatted_timestamps = []

    for ts in timestamps:
        formatted_timestamps.append(datetime.strptime(ts, timestamp_format))
    
    return formatted_timestamps

def timezone_correction(timestamp: list[datetime], correction_amount: int = 3) -> list[datetime]:
    """
    Смещает время в полученном списке объектов datetime.datetime на заданое количество часов.

    Args:
        timestamp (list[datetime]): Список объектов datetime.datetime
        correction_amount (int, optional): Значение (в часах), на которое необходимо сдвинуть время.
            По умолчанию равно 3 - смещение для часового пояса Москвы относительно GMT+0
    
    Returns:
        list[datetime]: Список объектов datetime.datetime со смещением на заданное количество часов.
    
    Example:
        >>> timezone_correction([datetime(1900, 1, 1, 15, 23), datetime(1900, 1, 1, 18, 10)], 3)
        [datetime.datetime(1900, 1, 1, 18, 23), datetime.datetime(1900, 1, 1, 21, 10)]
    """
    # При помощи timedelta задаём количество часов, на которые будет смещено время.
    new_time = timedelta(hours=correction_amount)

    corrected_timestamps = []

    # Проходимся по всем объектам datetime.datetime и смещаем время. Добавляем результат в итоговый список.
    for dt in timestamp:
        corrected_dt = dt + new_time
        corrected_timestamps.append(corrected_dt)
    
    return corrected_timestamps

def compose_report(weather_data: dict) -> dict:
    """
    Составляет текст отчёта об астрономической видимости.

    Парсит предварительно подготовленные метео-данные о каждом дне и на их основе формирует отчёт.

    Args:
        weather_data (dict): Словарь с метео-данными на запрошенное количество дней
    
    Returns:
        dict: Словарь с двумя парами ключ-значение - статус формирования отчёта и результат. В случае успешного формирования отчёта статус success, и в сообщении передаётся тело отчёта. В случае ошибки - статус "error", а в сообщении описание ошибки. 

    Examples:
        (см. лог)
    """
    result_status = ""
    result_message = ""

    output_str = f"""
Прогноз астрономической видимости.
Дата и время составления отчёта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    """
    total_days = 0

    for day in weather_data.keys():
        if not weather_data[day]["date_time"]:
            pass
        else:
            total_days += 1
            day_report = f"""
    Дата: {day.strftime("%d.%m.%Y")}
    Заход Солнца: {str(weather_data[day]["sunset"].strftime('%H:%M'))}
    Освещённость Луны ночью: {weather_data[day]["moon_illumination"]}%
    Фаза Луны: {weather_data[day]["moon_phase"]}
    Время с облачностью не более {CLOUDINESS_FILTER}%:
    """

            cloudiness_data = weather_data[day]["date_time"]

            for hour in cloudiness_data:
                cloudiness = f"""   {hour.strftime('%H:%M')} - {cloudiness_data[hour]}%
    """
                # Если день сегодняшний, и время меньше текущего (т.е. уже прошло), то не добавляем это в отчёт
                if day == datetime.now().date() and hour <= datetime.now().time():
                    pass
                else:
                    day_report += cloudiness
            output_str += day_report

    if total_days == 0:
        result_status = "error"
        result_message = "No data matching the specified criteria was found."
    else:
        result_status = "success"
        result_message = output_str

    result = {"status": result_status, "message" : result_message}

    return result