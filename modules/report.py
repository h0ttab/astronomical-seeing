import datetime
from modules.config_loader import CLOUDINESS_FILTER
from modules.utils import log
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('./resources'))
template = env.get_template('report_template.j2')

def compose_report(weather_data: dict) -> dict:
    """
    Формирует текстовый отчёт на основе шаблона Jinja2

    Входные данные представляют собой предварительно обработанный словарь с данными о погоде, сгруппированными по дням.
    В функции предусмотрена валидация на наличие данных в отчёте, чтобы избежать появление "пустых" дней.

    Args:
        weather_data (dict): Словарь с данными об облачности, времени захода Солнца, освещённости и фазе Луны

    Returns:
        dict: Словарь со статусом формирования отчёта (error или success) и сообщением, которое в случае
            успешного формирования отчёта содержит сам отчёт, или же с сообщением об ошибке, если
            отчёт не был сформирован.
    """
    current_time = str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
    is_data_present = False

    # Проверяем, есть ли данные для отчёта
    for day in weather_data.keys():
        if weather_data[day]["date_time"]:
            is_data_present = True
    
    # Если есть, то формируем отчёт
    if is_data_present:
        rendered_template = template.render(weather_data=weather_data, current_time=current_time, CLOUDINESS_FILTER=CLOUDINESS_FILTER)
        log(event_type="INFO", message="Сформирован отчёт", data=rendered_template)
        return {"status": "success", "message": rendered_template}
    
    # Если данных нет, то возвращаем статус с ошибкой
    else:
        log(event_type="WARNING", message="Отчёт не сформирован. Недостаточно данных", data="")
        return {"status": "error", "message": "Отчёт не сформирован. Недостаточно данных"}