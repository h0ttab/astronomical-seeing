import yaml
from datetime import datetime

# Функция для загрузки конфигурации из YAML
def load_config(config_path='./debug/config.yml'):
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

# Загружаем конфиг
config = load_config()

# Доступ к переменным
FORECAST_DAYS = config['FORECAST_DAYS']
TIMEZONE_CORRECTION_AMOUNT = config['TIMEZONE_CORRECTION_AMOUNT']
CLOUDINESS_FILTER = config['CLOUDINESS_FILTER']
TIME_FILTER = datetime.strptime(config['TIME_FILTER'], "%H:%M").time()
LOGS_PATH = config["LOGS_PATH"]
BOT_TOKEN = config["BOT_TOKEN"]
API_KEY = config["API_KEY"]
CHAT_ID = config["CHAT_ID"]
TIMEZONE = config["TIMEZONE"]
LATITUDE = config["LATITUDE"]
LONGITUDE = config["LONGITUDE"]