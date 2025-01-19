import uuid

from datetime import datetime, timedelta
from modules.config_loader import LOGS_PATH

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

def log(event_type: str, message: str, data: any = None) -> None:
    """
    Записывает данные в лог-файл с указанием типа события и сообщения.

    Эта функция записывает переданные данные в лог-файл, добавляя информацию о типе события, 
    описание события и саму информацию, а так же уникальный ID записи. Запись будет содержать текущую дату и время, тип события,
    сообщение и переданные данные. Если данные не переданы, то эта часть будет пропущена. 
    После записи выводится сообщение о количестве добавленных записей.

    Args:
        event_type (str): Тип события, который будет добавлен в лог (например, "INFO", "ERROR", "WARNING").
        message (str): Описание события, которое будет прикреплено к данным.
        data (any, optional): Данные любого типа, которые будут записаны в лог. 
            Если данные не переданы, эта часть будет пропущена.

    Returns:
        None

    Example:
        >>> log(event_type="INFO", message="Process started", data={"key": "value"})
        Запись в лог-файл с типом события "INFO" и сообщением "Process started" будет добавлена.
    """
    
    #Открываем лог-файл в режиме добавления новых данных
    with open(f"{LOGS_PATH + today_date}.log", "a", encoding="utf-8") as file:
        
        file.write(f"Timestamp: {datetime.now()}\n")
        file.write(f"Record UID: {str(uuid.uuid4())}\n")
        file.write(f"Event type: {event_type}\n")
        file.write(f"Message: {message}\n")
        if data:
            file.write(f"Data:\n{data}\n")
        file.write("\n")

def log_flush() -> None:
    """
    Очищает лог-файл. 
    
    Очищает лог, выводит в консоль сообщение о том, что лог очищен.
    
    Args:
        None
    
    Returns:
        None

    Example:
        >>> log_flush()
        "Log file has been cleared"

    """
    # Открываем лог-файл в режиме перезаписи и записываем туда пустую строку,
    # полностью стирая всё предыдущее содержимое
    log = open(f"{LOGS_PATH + today_date}.log", "w", encoding="utf-8")
    log.write("")
    log.close()

    print("Log file has been cleared")

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