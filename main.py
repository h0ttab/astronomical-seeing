import sys
import traceback
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from modules.data_processing.weather import process_weather_data, outdated_data_filter
    from modules.data_presentation import report
    from modules.data_providers.api import get_clouds_data, get_sun_moon_data
    from modules.data_presentation import telegram
# If an error occurs during module initialization, print it to the console and terminate the program.
except Exception as error:
    logging.error(error)
    sys.exit(1)


def main():
    clouds_data = get_clouds_data()
    sun_moon_data = get_sun_moon_data()
    filtered_clouds_data = outdated_data_filter(clouds_data["date_time"], clouds_data["cloudiness"])
    processed_data = process_weather_data(filtered_clouds_data, sun_moon_data)
    composed_report = report.compose_report(processed_data)

    # If the report was composed successfully, send it to the bot
    if composed_report["status"] == "success":
        telegram.bot_send_message(composed_report["message"])

    return composed_report


if __name__ == "__main__":
    try:
        main()
    # If an error occurs anywhere in the main flow, this handler will catch it.
    # Print it to the console, send it to the bot if possible, and terminate the program.
    except Exception:
        error_traceback = traceback.format_exc()
        logging.error(error_traceback)
        telegram.bot_send_message(f"An error occurred: \n {error_traceback}")
        sys.exit(1)