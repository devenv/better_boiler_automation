from typing import List

from modules.weather.weather_data import WeatherData


class Sun:

    def __init__(self, config: dict):
        self.config = config

    def output(self, weather_data: List[WeatherData]) -> float:
        return sum(self._energy_at_hour(data) for data in weather_data) / len(weather_data) * self.config['hours_ago_to_consider'] * self.config['sun_nerfer']

    def _energy_at_hour(self, weather_data: WeatherData):
        sunrise_hour = weather_data.sunrise_hour
        sunset_hour = weather_data.sunset_hour
        if weather_data.hour < sunrise_hour or weather_data.hour > sunset_hour:
            return 0
        mid = (sunset_hour - sunrise_hour) / 2
        sun_angle_ratio = 1 - abs(weather_data.hour - (mid + sunrise_hour)) / mid
        return weather_data.solar_energy * sun_angle_ratio * self.config['sun_receiving_area_in_sq_meters']