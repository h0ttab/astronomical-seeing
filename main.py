from modules.weather import get_clouds_data, get_sun_moon_data, process_weather_data
from modules.report import compose_report
from modules.config_loader import BOT_TOKEN, CHAT_ID
import requests

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
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": result["message"]
        }
        requests.get(url, payload)