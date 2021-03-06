from datetime import datetime, timedelta
import json
import requests

from modules.calendar_sync.calendar_sync import TIME_ZONE
from modules.weather.weather_data import WeatherData

from utils.secrets import load_string


class WeatherProvider:

    open_weather_api_key = load_string('weather_api_key')
    visualcrossing_api_key = load_string('visualcrossing_api_key')
    location = load_string('my_location')

    HOURS_TO_LOOK_BACK = 8

    def get_weather_data(self) -> WeatherData:
        visualcrossing_data = json.loads(requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{self.location}?unitGroup=metric&include=hours%2Ccurrent&key={self.visualcrossing_api_key}&contentType=json').text)
        current_weather = self._visualcrossing_to_weather_data(visualcrossing_data)
        return current_weather
        
    def _visualcrossing_to_weather_data(self, weather: dict) -> WeatherData:
        current_data = weather['currentConditions']
        sunrise_hour = int(current_data['sunrise'].split(':')[0])
        sunset_hour = int(current_data['sunset'].split(':')[0])
        now = datetime.utcnow() + timedelta(hours=TIME_ZONE * 2)  # looks like a bug in visualcrossing, all hours are shifted by another TZ, solar energy doesn't fit the sunset/sunrise otherwise
        date_now = now.strftime("%Y-%m-%d")
        hour_now = now.strftime("%H:00:00")
        today_data = [day for day in weather['days'] if day['datetime'] == date_now][0]
        last_hour_data = [hour for hour in today_data['hours'] if hour['datetime'] == hour_now][0]
        solar_energy = last_hour_data['solarenergy'] or 0
        solar_energy = solar_energy / 3.6  # kWh

        return WeatherData(
            hour=now.hour,
            temperature=current_data['temp'],
            clouds=current_data['cloudcover'],
            feels_like=current_data['feelslike'],
            visibility=current_data['visibility'],
            humidity=current_data['humidity'],
            precipitation=current_data['precip'] or 0,
            pressure=current_data['pressure'],
            wind_speed=current_data['windspeed'],
            solar_energy=last_hour_data['solarenergy'] or 0,
            solar_radiation=last_hour_data['solarradiation'] or 0,
            sunrise_hour=sunrise_hour,
            sunset_hour=sunset_hour,
        )