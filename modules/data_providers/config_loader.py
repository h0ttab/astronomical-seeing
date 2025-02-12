import yaml
from datetime import datetime
from schema import And, Or, Regex, Schema, SchemaError

# Функция для загрузки конфигурации из YAML
def load_config(config_path='./config.yml'):
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

# Загружаем конфиг
try:
    config = load_config()
# Если не удалось загрузить файл конфигурации, вызываем ошибку FileNotFoundError
except FileNotFoundError:
    raise FileNotFoundError("Ошибка при загрузке файла конфигурации: файл не найден.")
    

# Описание схемы конфига - какие ключи должны быть, какие типы данных они должны содержать, и т.д.
config_schema = Schema({
    "FORECAST_DAYS": And(int,Or(lambda days_requested: 1 <= days_requested <= 10, error=f"Количество запрашиваемых дней для прогноза должно быть от 1 до 10.")),
    "CLOUDINESS_FILTER": And(int, Or(lambda cloudiness_percent: 0 <= cloudiness_percent <= 100, error="Максимально приемлемый показатель облачности (%) должен быть целым числом от 0 до 100.")),
    "TIME_FILTER": Or(Regex(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'), error="Время в параметре TIME_FILTER должно быть указано в 24-часовом формате, например 03:00 ."),
    "BOT_TOKEN": str,
    "API_KEY": str,
    "CHAT_ID": str,
    "TIMEZONE": Or(Regex(r"^[A-Z][a-zA-Z]*\/[A-Z][a-zA-Z]*$"), error="Часовой пояс должен указываться в формате Название_региона/Город , например Europe/Moscow."),
    "LATITUDE": And(Or(float, int), Or(lambda latitude: -90 <= latitude <= 90, error="Широта должна быть представлена целым или дробным числом от -90° до +90°")),
    "LONGITUDE": And(Or(float, int), Or(lambda longitude: -180 <= longitude <= 180, error="Долгота должна быть представлена целым или дробным числом от -180° до +180°")),
})

try:
    # Валидация конфига
    config_schema.validate(config)
    
    # Доступ к переменным
    FORECAST_DAYS = config['FORECAST_DAYS']
    CLOUDINESS_FILTER = config['CLOUDINESS_FILTER']
    TIME_FILTER = datetime.strptime(config['TIME_FILTER'], "%H:%M").time()
    BOT_TOKEN = config["BOT_TOKEN"]
    API_KEY = config["API_KEY"]
    CHAT_ID = config["CHAT_ID"]
    TIMEZONE = config["TIMEZONE"]
    LATITUDE = config["LATITUDE"]
    LONGITUDE = config["LONGITUDE"]
# Если конфиг не прошёл валидацию, вызываем ошибку SchemaError
except SchemaError as error:
    raise SchemaError(f"Ошибка при загрузке конфигурации: {error}")