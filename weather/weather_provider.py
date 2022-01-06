from datetime import datetime, timedelta
import os
import sys
from typing import List


from dataclasses import dataclass
import pyowm
from pyowm.utils import formatting
from pyowm.weatherapi25.weather import Weather

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()


def load_api_key():
    with open(os.path.join(sys.path[0], 'weather/weather_api_key.txt')) as f:
        return f.readline().strip()

def load_location():
    with open(os.path.join(sys.path[0], 'weather/my_location.txt')) as f:
        return f.readline().strip()

@dataclass
class WeatherData:
    temperature: float
    clouds: int
    #hours_in_day: int


class WeatherProvider:

    api_key = load_api_key()
    location = load_location()

    HOURS_TO_LOOK_BACK = 8

    def get_weather_data(self) -> List[WeatherData]:
        owm = pyowm.OWM(self.api_key)
        mgr = owm.weather_manager()
        city = owm.city_id_registry().locations_for(self.location)[0]
        current_weather = self.weather_to_weather_data(mgr.one_call_history(lat=city.lat, lon=city.lon, dt=formatting.to_UNIXtime(datetime.today() - timedelta(hours=1))).current)

        metrics.gauge("current_weather.temperature", current_weather.temperature)
        metrics.gauge("current_weather.clouds", current_weather.clouds)
        logger.info(f"Current weather: temperature - {current_weather.temperature}, clouds - {current_weather.clouds}")

        results = [current_weather]

        for i in range(2, self.HOURS_TO_LOOK_BACK + 1):
            weather = self.weather_to_weather_data(mgr.one_call_history(lat=city.lat, lon=city.lon, dt=formatting.to_UNIXtime(datetime.now() - timedelta(hours=i))).current)
            results.append(weather)
            metrics.gauge("previous_weather.temperature", weather.temperature, tags={'hours_ago': str(i)})
            metrics.gauge("previous_weather.clouds", weather.clouds, tags={'hours_ago': str(i)})

        return results
        
    def weather_to_weather_data(self, weather: Weather) -> WeatherData:
        return WeatherData(
            temperature=weather.temperature('celsius')['temp'],
            clouds=weather.clouds,
            #hours_in_day=int((weather.sunset_time() - weather.sunrise_time()) / 60 / 60),
        )
