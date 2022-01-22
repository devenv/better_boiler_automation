from datetime import timedelta

from data_stores.weather.weather_data_stores import WeatherDataStore
from modules.module import Module
from modules.weather.visual_crossing_provider import WeatherProvider

from metrics.metrics import Metrics
from utils.logger import get_logger
from utils.secrets import load_dict

logger = get_logger()
metrics = Metrics()


class WeatherModule(Module):
    
    NAME ='weather'
    SCHEDULE = "2,7,12,17,22,27,32,37,42,47,52,57 * * * *"

    def run(self):
        super().run()

        config = load_dict("calculator_config")

        weather = WeatherProvider().get_weather_data()

        logger.info(f"T: {weather.temperature:.2f}, SE: {weather.solar_energy:.2f}")
        metrics.gauge("current_weather.temperature", weather.temperature)
        metrics.gauge("current_weather.clouds", weather.clouds)
        metrics.gauge("current_weather.feels_like", weather.feels_like)
        metrics.gauge("current_weather.visibility", weather.visibility)
        metrics.gauge("current_weather.humidity", weather.humidity)
        metrics.gauge("current_weather.precipitation", weather.precipitation)
        metrics.gauge("current_weather.pressure", weather.pressure)
        metrics.gauge("current_weather.wind_speed", weather.wind_speed)
        metrics.gauge("current_weather.solar_energy", weather.solar_energy)
        metrics.gauge("current_weather.solar_radiation", weather.solar_radiation)

        WeatherDataStore(freshness=timedelta(hours=config['hours_ago_to_consider'])).add_value(weather)