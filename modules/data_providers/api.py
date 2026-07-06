from modules.data_processing.weather import moon_illumination
from modules.data_providers.config_loader import FORECAST_DAYS, API_KEY, TIMEZONE, LATITUDE, LONGITUDE

from datetime import datetime

import requests
from requests.exceptions import RequestException

# Base URL for the weather service API
API_BASE_URL = "http://my.meteoblue.com/packages/"

# Base (required) parameters for GET request sent with every API call.
REQUEST_COMMON_PARAMS = {
    "apikey": API_KEY,
    "tz": TIMEZONE,
    "forecast_days": FORECAST_DAYS,
    "format": "json",
    "lat": LATITUDE,
    "lon": LONGITUDE,
}


def fetch(endpoint: str, add_params=None) -> dict:
    """
    Sends a GET request to the API and receives data.

    Requests (GET) and receives data from the API service. Returns a JSON object (dictionary) with the API response data.

    Args:
        endpoint (str): The specific API service endpoint, appended to the end of the base URL
            defined as the global variable API_BASE_URL.
        add_params (dict, optional): Additional set of GET request parameters for the API service.
            Added to the base parameters defined in the global variable REQUEST_COMMON_PARAMS.

    Returns:
        dict: Returns the received data as a dictionary (from JSON).

    Example:
        >>> fetch("/api_service", {"city":"Moscow"})
        {"response_code":200, "requested_city:"Moscow", "current_time":"21:30"}
    """

    if add_params is None:
        add_params = {}
    url = API_BASE_URL + endpoint.lstrip(" /")
    # Merge dictionaries with required and optional request parameters using the "|" operator
    params = add_params | REQUEST_COMMON_PARAMS
    try:
        data = requests.get(url, params).json()
        # If the API returned an error, raise a RequestException
        if data.get("error") == True:
            raise RequestException(data['error_message'])
        return data
    # In case of another error (no connection to API), raise a RequestException
    except RequestException as error:
        raise RequestException(f"An error occurred while requesting data from the server: {error}")


def get_clouds_data() -> dict:
    """
    Requests cloudiness data via API.
    Requests cloudiness data, parses the date and time data from strings (str) to datetime objects.

    Returns:
        dict: Dictionary containing two key-value pairs - date_time and cloudiness, containing hourly cloud cover data
            for the entire requested period. Each entry in the date_time list corresponds to the cloudiness entry at the same index.

    Example:
    >>> get_clouds_data()
        {'date_time': [datetime.datetime(2025, 1, 9, 0, 0), datetime.datetime(2025, 1, 9, 1, 0)], 'cloudiness': [65, 32]}
    """

    data = fetch("/clouds-1h", {"windspeed": "kmh", "temperature": "C"})["data_1h"]

    date_time = [datetime.strptime(timestamp, "%Y-%m-%d %H:%M") for timestamp in data["time"]]
    cloudiness = data["totalcloudcover"]

    return {
        "date_time": date_time,
        "cloudiness": cloudiness,
    }


def get_sun_moon_data() -> dict:
    """
    Requests sunset/sunrise and moon data via API, calculates moon illumination percentage.
    Requests daily sun and moon data, and (if necessary) adjusts sunset time according to the specified timezone.
    Calculates moon illumination percentage at midnight at the end of each day.

    Returns:
        dict: Dictionary containing 4 datasets - date, sunset, moon_illumination, moon_phase_name.
            Each list element corresponds to elements in other lists at the same index.

    Example:
        >>> get_sun_moon_data()
            {'date': [datetime.datetime(2025, 1, 9, 0, 0)], 'sunset': [datetime.datetime(1900, 1, 1, 16, 20)],'moon_illumination': [79.8], 'moon_phase_name': ['waxing gibbous']}
    """
    data = fetch("/sunmoon")["data_day"]

    data["time"] = [datetime.strptime(timestamp, "%Y-%m-%d") for timestamp in data["time"]]
    data["sunset"] = [datetime.strptime(timestamp, "%H:%M") for timestamp in data["sunset"]]

    moon_illumination_percentage = moon_illumination(data["moonilluminatedfraction"], data["moonphasename"])

    return {
        "date": data["time"],
        "sunset": data["sunset"],
        "moon_illumination": moon_illumination_percentage,
        "moon_phase_name": data["moonphasename"]
    }