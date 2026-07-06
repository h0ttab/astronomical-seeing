import yaml
from datetime import datetime
from schema import And, Or, Regex, Schema, SchemaError


# Function to load configuration from YAML
def load_config(config_path='./config.yml'):
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


# Load the config
try:
    config = load_config()
# If the configuration file could not be loaded, raise a FileNotFoundError
except FileNotFoundError:
    raise FileNotFoundError("Error loading configuration file: file not found.")

# Config schema description - what keys must be present, what data types they should contain, etc.
config_schema = Schema({
    "FORECAST_DAYS": And(int, Or(lambda days_requested: 1 <= days_requested <= 10,
                                 error="Number of forecast days requested must be between 1 and 10.")),
    "CLOUDINESS_FILTER": And(int, Or(lambda cloudiness_percent: 0 <= cloudiness_percent <= 100,
                                     error="Maximum acceptable cloud cover percentage must be an integer between 0 and 100.")),
    "TIME_FILTER": Or(Regex(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'),
                      error="Time in TIME_FILTER must be in 24-hour format, e.g., 03:00."),
    "BOT_TOKEN": str,
    "API_KEY": str,
    "CHAT_ID": str,
    "TIMEZONE": Or(Regex(r"^[A-Z][a-zA-Z]*\/[A-Z][a-zA-Z]*$"),
                   error="Timezone must be specified in Region/City format, e.g., Europe/Moscow."),
    "LATITUDE": And(Or(float, int), Or(lambda latitude: -90 <= latitude <= 90,
                                       error="Latitude must be an integer or float between -90° and +90°.")),
    "LONGITUDE": And(Or(float, int), Or(lambda longitude: -180 <= longitude <= 180,
                                        error="Longitude must be an integer or float between -180° and +180°.")),
})

try:
    # Validate the config
    config_schema.validate(config)

    # Access variables
    FORECAST_DAYS = config['FORECAST_DAYS']
    CLOUDINESS_FILTER = config['CLOUDINESS_FILTER']
    TIME_FILTER = datetime.strptime(config['TIME_FILTER'], "%H:%M").time()
    BOT_TOKEN = config["BOT_TOKEN"]
    API_KEY = config["API_KEY"]
    CHAT_ID = config["CHAT_ID"]
    TIMEZONE = config["TIMEZONE"]
    LATITUDE = config["LATITUDE"]
    LONGITUDE = config["LONGITUDE"]
# If the config validation fails, raise a SchemaError
except SchemaError as error:
    raise SchemaError(f"Configuration error: {error}")