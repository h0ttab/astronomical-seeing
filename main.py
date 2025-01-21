from modules.data_processing.weather import process_weather_data, outdated_data_filter
from modules.data_presentation import telegram
from modules.data_presentation import report
from modules.data_providers.api import get_clouds_data, get_sun_moon_data

def main():
    clouds_data = get_clouds_data()
    sun_moon_data = get_sun_moon_data()
    filtered_clouds_data = outdated_data_filter(clouds_data["date_time"], clouds_data["cloudiness"])
    processed_data = process_weather_data(filtered_clouds_data, sun_moon_data)
    composed_report = report.compose_report(processed_data)
    
    #Если успешно сформирован отчёт, отправляем его в бот
    if composed_report["status"] == "success":
        telegram.bot_send_message(composed_report["message"])

    return composed_report

if __name__ == "__main__":
    main()