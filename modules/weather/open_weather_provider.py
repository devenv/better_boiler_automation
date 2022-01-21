from datetime import datetime, timedelta
import pyowm
from pyowm.utils import formatting
from pyowm.weatherapi25.weather import Weather

from modules.weather.weather_data import WeatherData

from utils.secrets import load_string


class WeatherProvider:

    api_key = load_string('weather_api_key')
    location = load_string('my_location')

    HOURS_TO_LOOK_BACK = 8

    def get_weather_data(self) -> WeatherData:
        owm = pyowm.OWM(self.api_key)
        mgr = owm.weather_manager()
        city = owm.city_id_registry().locations_for(self.location)[0]
        open_weather_data = mgr.one_call_history(lat=city.lat, lon=city.lon, dt=formatting.to_UNIXtime(datetime.today() - timedelta(hours=1))).current
        current_weather = self._open_weather_to_weather_data(open_weather_data)
        return current_weather
        
    def _open_weather_to_weather_data(self, weather: Weather) -> WeatherData:
        return WeatherData(
            temperature=weather.temperature('celsius')['temp'],
            clouds=weather.clouds,
            feels_like=weather.temperature('celsius')['feels_like'],
            visibility=weather.visibility_distance,
            humidity=weather.humidity,
            precipitation=weather.precipitation_probability or 0,
            pressure=weather.pressure['press'],
            wind_speed=weather.wind()['speed'],
            solar_energy=0,
            solar_radiation=0,
        )