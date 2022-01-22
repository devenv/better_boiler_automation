from datetime import datetime
from typing import List

from modules.weather.weather_data import WeatherData


class Sun:

    def __init__(self, config: dict):
        self.config = config

    def output(self, weather_data: List[WeatherData]) -> float:
        now = datetime.now()
        current_hour = now.hour
        sunrise_hour = weather_data[0].sunrise_hour
        sunset_hour = weather_data[0].sunset_hour
        if current_hour < sunrise_hour or current_hour > sunset_hour:
            return 0
        sunrise_hour_time = datetime(now.year, now.month, now.day, sunrise_hour, 0, 0)
        sun_angle_ratio = (now.timestamp() - sunrise_hour_time.timestamp()) / 60 / 60 / (sunset_hour - sunrise_hour)
        return sun_angle_ratio * sum(data.solar_energy for data in weather_data) / len(weather_data) * self.config['hours_ago_to_consider'] * self.config['sun_receiving_area_in_sq_meters'] * self.config['sun_nerfer']