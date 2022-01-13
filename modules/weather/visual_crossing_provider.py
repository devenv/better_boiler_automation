import json
import requests

from modules.weather.weather_data import WeatherData

from utils.secrets import load_string


class WeatherProvider:

    open_weather_api_key = load_string('weather_api_key')
    visualcrossing_api_key = load_string('visualcrossing_api_key')
    location = load_string('my_location')

    HOURS_TO_LOOK_BACK = 8

    def get_weather_data(self) -> WeatherData:
        visualcrossing_data = json.loads(requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{self.location}?unitGroup=metric&include=current&key={self.visualcrossing_api_key}&contentType=json').text)
        current_weather = self._visualcrossing_to_weather_data(visualcrossing_data['currentConditions'])
        return current_weather
        
    def _visualcrossing_to_weather_data(self, weather: dict) -> WeatherData:
        return WeatherData(
            temperature=weather['temp'],
            clouds=weather['cloudcover'],
            feels_like=weather['feelslike'],
            visibility=weather['visibility'],
            humidity=weather['humidity'],
            precipitation=weather['precip'] or 0,
            pressure=weather['pressure'],
            wind_speed=weather['windspeed'],
            wind_direction=weather['winddir'],
            solar_energy=weather['solarenergy'] or 0,
            solar_radiation=weather['solarradiation'] or 0,
        )