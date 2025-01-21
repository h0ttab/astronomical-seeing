from modules.data_processing.weather import get_clouds_data, get_sun_moon_data, process_weather_data
from modules.data_presentation.report import compose_report
from modules.data_presentation import telegram

def main():
    clouds_data = get_clouds_data()
    sun_moon_data = get_sun_moon_data()
    processed_data = process_weather_data(clouds_data, sun_moon_data)
    report = compose_report(processed_data)
    
    return report

if __name__ == "__main__":
    result = main()
    #Если успешно сформирован отчёт, отправляем его в бот
    if result["status"] == "success":
        telegram.bot_send_message(result["message"])