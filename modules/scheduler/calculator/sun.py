from typing import List

from modules.weather.weather_data import WeatherData


class Sun:

    def __init__(self, config: dict):
        self.config = config

    def output(self, weather_data: List[WeatherData]) -> float:
        return sum(data.solar_energy for data in weather_data) / len(weather_data) * 3600 * self.config['hours_ago_to_consider'] / 3.6 * self.config['sun_nerfer']