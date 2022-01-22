from datetime import timedelta
from typing import List

from data_stores.data_persisters import FreshDataStore
from modules.weather.weather_data import WeatherData


FRESHNESS = timedelta(hours=12)
MAX_SIZE = 100


class WeatherDataStore(FreshDataStore[WeatherData]):
    
    def __init__(self):
        super().__init__('weather', MAX_SIZE, FRESHNESS)
    
    def read_all_values_since(self, freshness: timedelta) -> List[WeatherData]:
        result = super().read_all_values_since(freshness)
        return [WeatherData.from_dict(data) for data in result]