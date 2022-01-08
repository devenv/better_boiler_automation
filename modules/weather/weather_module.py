from data_stores.weather.weather_data_stores import CloudsDataStore, TemperatureDataStore
from modules.module import Module
from modules.weather.weather_provider import WeatherProvider


class WeatherModule(Module):
    
    NAME ='weather'
    SCHEDULE = "2,7,12,17,22,27,32,37,42,47,52,57 * * * *"

    def run(self):
        super().run()
        weather = WeatherProvider().get_weather_data()
        TemperatureDataStore().add_value(weather.temperature)
        CloudsDataStore().add_value(weather.clouds)