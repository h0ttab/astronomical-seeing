import math

from datetime import time, datetime
from modules.data_providers.config_loader import TIME_FILTER, CLOUDINESS_FILTER


def moon_illumination(illumination_midday: list[float], phase_name: list[str]) -> list:
    """
    Calculates moon illumination at midnight based on midday illumination data and moon phase.

    Args:
        illumination_midday (list[float]): list of moon illumination values at midday. One value per day.
        phase_name (list[str]): list of moon phase names. One value per day.

    Returns:
        list: List of moon illumination values at midnight for each day.

    Example:
    >>> moon_illumination([15.4, 19.2], ["waxing crescent", "waxing crescent")
    [19.0, 23.1]
    """

    waxing = ["new", "waxing crescent", "first quarter", "waxing gibbous"]
    waning = ["full", "waning gibbous", "last quarter", "waning crescent"]
    result = []

    def process_data(noon_percentage: float, phase_name: str) -> float:
        """
        Calculates moon illumination at midnight based on midday illumination data and moon phase.

        Args:
            noon_percentage (float): moon illumination value at midday for a specific day.
            phase_name (str): Moon phase name for a specific day.

        Returns:
            float: moon illumination value at midnight for a specific day.

        Example:
        >>> process_data(15.4, "waxing crescent")
        19.0
        """

        # Convert phase name to lowercase for comparison
        phase_name = phase_name.lower()

        # Check if the phase name is valid and determine the moon phase
        if phase_name in waxing:
            is_waxing = True
        elif phase_name in waning:
            is_waxing = False
        else:
            raise ValueError("Invalid phase name. Please use one of the predefined phase names.")

        # Constants
        T = 29.53  # Synodic month (lunar cycle period) in days
        delta_t = 0.5  # Time difference in days (12 hours)

        # Convert illumination percentage to a fraction from 0 to 1
        P_t = noon_percentage / 100.0

        # Ensure the input percentage is within the valid range
        if not (0 <= P_t <= 1):
            raise ValueError("Illumination percentage must be between 0 and 100.")

        # Step 1: Calculate the initial phase angle θ at midday
        cos_theta = 1 - 2 * P_t
        # Ensure the value is within the valid range for arccos
        cos_theta = min(max(cos_theta, -1), 1)
        theta = math.acos(cos_theta)

        # Step 2: Determine the phase angle θ(t) depending on the moon phase
        if is_waxing:
            theta_t = theta
        else:
            theta_t = 2 * math.pi - theta

        # Step 3: Calculate the change in phase angle over Δt
        delta_theta = 2 * math.pi * (delta_t / T)

        # Step 4: Calculate the phase angle at midnight
        theta_t_plus_delta = theta_t + delta_theta
        # Normalize the angle to stay within the range 0 to 2π
        theta_t_plus_delta = theta_t_plus_delta % (2 * math.pi)

        # Step 5: Calculate the illumination percentage at midnight
        P_t_plus_delta = 0.5 * (1 - math.cos(theta_t_plus_delta))
        illumination_percentage = P_t_plus_delta * 100  # Convert to percentage

        # Append the result to the list, applying a correction factor of 0.98
        result.append(round(illumination_percentage * 0.98, 1))

    for i in range(len(illumination_midday)):
        process_data(illumination_midday[i], phase_name[i])

    return result


def is_time_in_range(range_from: time, range_to: time, timestamp_to_check: time) -> bool:
    """
    Checks whether a given time falls within the specified range, including crossing midnight.

    Args:
        range_from (datetime.time): Start point of the time range to check.
        range_to (datetime.time): End point of the time range to check.
        timestamp_to_check (datetime.time): The timestamp being checked against the range.

    Returns:
        bool: Returns True if the timestamp is within the range, otherwise False.

    Example:
        >>> is_time_in_range(datetime.time(16,0), datetime.time(3,0), datetime.time(19,41))
        True
    """

    # Check that the timestamp meets one of the criteria: greater than or equal to the range start OR greater than or equal to 00:00 and less than or equal to the range end
    return timestamp_to_check >= range_from or time(0, 0) <= timestamp_to_check <= range_to


def filter_cloudiness_data(data: dict, sunset: time) -> dict:
    """
    Filters date/time and cloudiness data.

    Filters the date/time and cloudiness data, keeping only entries that meet the criteria: time - from sunset to $TIME_FILTER, cloudiness - not exceeding $CLOUDINESS_FILTER.

    Args:
        data (dict): dictionary of time:cloudiness values for a specific day
        sunset (datetime.time): information about sunset time on that day. Start point of the filtering range.

    Returns:
        dict: dictionary with filtered date_time and cloudiness values
    """
    # Create an empty dictionary to store filtered data
    filtered_data = {}

    # Iterate over all time and cloudiness values in the dictionary, copying pairs that fall within the specified time range and do not exceed the maximum acceptable cloudiness
    for date_time, cloudiness in zip(data.keys(), data.values()):
        if is_time_in_range(sunset, TIME_FILTER, date_time) and cloudiness <= CLOUDINESS_FILTER:
            filtered_data[date_time] = cloudiness

    return filtered_data


def split_cloudiness_by_days(datetime: dict) -> dict:
    """
    Groups date/time and cloudiness data by day.

    Splits two lists (date+time and cloudiness) into a dictionary containing cloudiness data grouped by day for each hour.

    Args:
        datetime (dict): Dictionary containing date_time (datetime.datetime - full date and time) and cloudiness lists.

    Returns:
        dict: Dictionary containing time and cloudiness values grouped by day.

    Example:
        >>> split_cloudiness_by_days({"date_time":[datetime.datetime(2001,12,6,15,0), datetime.datetime(2001,12,6,16,0)], "cloudiness":[15,25]})
        {datetime.date(2001, 12, 6): {'date_time': {datetime.time(15, 0): 15, datetime.time(16, 0): 25}}}
    """
    grouped_cloudiness = {}

    # Iterate over all pairs of date/time : cloudiness
    for dt, cl in zip(datetime["date_time"], datetime["cloudiness"]):
        # If the grouping key for the date (one specific day) doesn't exist yet, create it.
        if dt.date() not in grouped_cloudiness:
            grouped_cloudiness[dt.date()] = {"date_time": {}}
        # Split the datetime.datetime object into date and time, and add them to the corresponding day's group.
        grouped_cloudiness[dt.date()]["date_time"][dt.time()] = cl

    return grouped_cloudiness


def process_weather_data(clouds_data: dict, moon_data: dict) -> dict:
    """
    Processes and compiles cloudiness and moon data.

    Processes and compiles hourly cloudiness data, moon phase and illumination, sunset time into a single dictionary grouped by day.

    Args:
        clouds_data (dict): contains cloudiness data obtained from get_clouds_data()
        moon_data (dict): contains moon and sunset data obtained from get_sun_moon_data()

    Returns:
        dict: Final dictionary containing processed and merged data from both inputs.

    Example:
        >>> 1. Groups clouds_data by day
        >>> 2. Then, for each grouping day:
            >>> 2.1 Filters time and cloudiness data, keeping only entries that fall within the "from sunset to 03:00 AM (default)" range.
            >>> 2.2 Adds the sunset time entry
            >>> 2.3 Adds the moon illumination percentage at midnight entry
            >>> 2.4 Adds the moon phase name entry
        >>> 3. Returns the final dictionary broken down by day
    """

    # Moon phase names with translation
    moon_phase_translation = {
        "new": "New Moon - \U0001F311",
        "waxing crescent": "Waxing Crescent - \U0001F312",
        "first quarter": "First Quarter - \U0001F313",
        "waxing gibbous": "Waxing Gibbous - \U0001F314",
        "full": "Full Moon - \U0001F315",
        "waning gibbous": "Waning Gibbous - \U0001F316",
        "last quarter": "Last Quarter - \U0001F317",
        "waning crescent": "Waning Crescent - \U0001F318"
    }

    clouds_data = split_cloudiness_by_days(clouds_data)

    for day, sunset, moon_illumination_data, moon_phase in zip(clouds_data, moon_data["sunset"],
                                                               moon_data["moon_illumination"],
                                                               moon_data["moon_phase_name"]):
        clouds_data[day]["date_time"] = filter_cloudiness_data(clouds_data[day]["date_time"], sunset.time())
        clouds_data[day]["sunset"] = sunset.time()
        clouds_data[day]["moon_illumination"] = moon_illumination_data
        clouds_data[day]["moon_phase"] = moon_phase_translation[moon_phase]

    # Remove the last element of the dictionary, as it contains 00:00 for the day after the last requested day. No sun/moon data is requested for that date, so this dictionary element is unnecessary.
    clouds_data.popitem()

    # Remove all days with empty cloudiness information (discarded by the filter).
    # The list(dict.keys()) construct iterates over a copy of the dictionary keys,
    # allowing modification of the dictionary without getting an error about changing dictionary size during iteration.
    for day in list(clouds_data.keys()):
        if not clouds_data[day]["date_time"]:
            clouds_data.pop(day)

    return clouds_data


def outdated_data_filter(date_time: list[datetime], cloudiness: list[int]) -> dict:
    """
    Filters time/cloudiness data, removing outdated entries.

    Removes data for times that have already passed relative to the moment of report generation.
    Iterates through both input lists in parallel, and if a timestamp is equal to or greater than the current time, that timestamp is moved to the resulting "cleaned" list, and the corresponding cloudiness value for that timestamp is moved to the analogous resulting list for cloudiness.

    Args:
        date_time (list[datetime]): List of timestamps
        cloudiness (list[int]): List of cloudiness percentages

    Returns:
        list: Two lists with filtered time and cloudiness values.
    """
    filtered_date_time = []
    filtered_cloudiness = []

    for dt_obj, cloudiness in zip(date_time, cloudiness):
        if dt_obj.date() == dt_obj.now().date() and dt_obj.time() <= dt_obj.now().time():
            pass
        else:
            filtered_date_time.append(dt_obj)
            filtered_cloudiness.append(cloudiness)
    return {
        "date_time": filtered_date_time,
        "cloudiness": filtered_cloudiness,
    }