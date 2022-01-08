from data_stores.weather.weather_data_stores import CloudsDataStore, TemperatureDataStore
from modules.module import Module
from modules.weather.weather_provider import WeatherProvider


class WeatherModule(Module):
    
    NAME ='weather'
    SCHEDULE = "*/15 * * * *"

    def run(self):
        weather = WeatherProvider().get_weather_data()
        TemperatureDataStore().add_value(weather.temperature)
        CloudsDataStore().add_value(weather.clouds)