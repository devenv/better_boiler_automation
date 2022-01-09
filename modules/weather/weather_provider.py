from datetime import datetime, timedelta


from dataclasses import dataclass
import pyowm
from pyowm.utils import formatting
from pyowm.weatherapi25.weather import Weather

from metrics.metrics import Metrics
from utils.logger import get_logger
from utils.secrets import load_string

logger = get_logger()
metrics = Metrics()


@dataclass
class WeatherData:
    temperature: float
    clouds: int


class WeatherProvider:

    api_key = load_string('weather_api_key')
    location = load_string('my_location')

    HOURS_TO_LOOK_BACK = 8

    def get_weather_data(self) -> WeatherData:
        owm = pyowm.OWM(self.api_key)
        mgr = owm.weather_manager()
        city = owm.city_id_registry().locations_for(self.location)[0]
        current_weather = self._weather_to_weather_data(mgr.one_call_history(lat=city.lat, lon=city.lon, dt=formatting.to_UNIXtime(datetime.today() - timedelta(hours=1))).current)

        metrics.gauge("current_weather.temperature", current_weather.temperature)
        metrics.gauge("current_weather.clouds", current_weather.clouds)
        logger.info(f"Temperature: {current_weather.temperature}")

        return current_weather
        
    def _weather_to_weather_data(self, weather: Weather) -> WeatherData:
        return WeatherData(
            temperature=weather.temperature('celsius')['temp'],
            clouds=weather.clouds,
            #hours_in_day=int((weather.sunset_time() - weather.sunrise_time()) / 60 / 60),
        )
