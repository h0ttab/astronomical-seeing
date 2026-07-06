import datetime
from modules.data_providers.config_loader import CLOUDINESS_FILTER
from jinja2 import Environment, FileSystemLoader, TemplateError

try:
    env = Environment(loader=FileSystemLoader('./resources'))
    template = env.get_template('report_template.j2')
except TemplateError as error:
    raise TemplateError


def compose_report(weather_data: dict) -> dict:
    """
    Generates a text report based on a Jinja2 template

    The input data is a pre-processed dictionary with weather data grouped by day.
    The function includes validation for data presence in the report to avoid empty days.

    Args:
        weather_data (dict): Dictionary with data on cloudiness, sunset time, moon illumination, and moon phase.

    Returns:
        dict: Dictionary with the report generation status (error or success) and a message containing the report itself if successful, or an error message if the report was not generated.
    """
    current_time = str(datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
    is_data_present = False

    # Check if there is data for the report
    for day in weather_data.keys():
        if weather_data[day]["date_time"]:
            # If there is data, set the flag to True
            is_data_present = True

    # If there is data, generate the report
    if is_data_present:
        try:
            rendered_template = template.render(weather_data=weather_data, current_time=current_time,
                                                CLOUDINESS_FILTER=CLOUDINESS_FILTER)
            return {"status": "success", "message": rendered_template}
        # If an error occurs during report generation, raise a TemplateError
        except TemplateError as error:
            raise TemplateError(f"An error occurred while rendering the template: {error}")

    # If there is no data, return an error status
    else:
        return {"status": "error", "message": "Report not generated. Insufficient data"}