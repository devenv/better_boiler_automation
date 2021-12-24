from datetime import datetime, timedelta
import os
import sys

from dataclasses import dataclass
import pyowm
from pyowm.utils import formatting


def load_api_key():
    with open(os.path.join(sys.path[0], 'weather_api_key.txt')) as f:
        return f.readline().strip()

def load_location():
    with open(os.path.join(sys.path[0], 'my_location.txt')) as f:
        return f.readline().strip()

@dataclass
class WeatherData:
    temperature: float
    clouds: int
    #hours_in_day: int


class WeatherProvider:

    api_key = load_api_key()
    location = load_location()
    HOURS_TO_LOOK_BACK = 4

    def get_weather_data(self):
        results = []
        owm = pyowm.OWM(self.api_key)
        mgr = owm.weather_manager()
        city = owm.city_id_registry().locations_for(self.location)[0]

        for i in range(self.HOURS_TO_LOOK_BACK):
            results.append(self.weather_to_weather_data(mgr.one_call_history(lat=city.lat, lon=city.lon, dt=formatting.to_UNIXtime(datetime.today() - timedelta(hours=1))).current))

        return results
        
    def weather_to_weather_data(self, weather):
        return WeatherData(
            temperature=weather.temperature('celsius')['temp'],
            clouds=weather.clouds,
            #hours_in_day=int((weather.sunset_time() - weather.sunrise_time()) / 60 / 60),
        )
