import json
import os
import sys
from typing import List

from weather.weather_provider import WeatherData

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()

def load_config():
    with open(os.path.join(sys.path[0], "calculator/calculator_config.json"), "r") as f:
        return json.load(f)


class Calculator:

    config = load_config()
    report_metrics: bool = False

    def calculate_for_all_intensities(self, weather: List[WeatherData]):
        self.report_metrics = True
        for intensity in range(1, 11):
            self.needed_hours_to_heat(weather, intensity)
        self.report_metrics = False

    def needed_hours_to_heat(self, weather: List[WeatherData], intensity: int) -> float:
        avg_temp = sum(data.temperature for data in weather) / len(weather)
        self._report_gauge("avg_temp", avg_temp, intensity)

        needed_temperature = self._needed_temperature(intensity)
        self._report_gauge("needed_temperature", needed_temperature, intensity)

        needed_energy = self._needed_energy(avg_temp, needed_temperature)
        self._report_gauge("needed_energy", needed_energy, intensity)

        delta_energy = needed_energy - self._sun_output(weather)
        self._report_gauge("delta_energy", delta_energy, intensity)

        if delta_energy <= 0:
            return 0

        hours_needed = self._needed_boiler_time(delta_energy)
        self._report_gauge("hours_needed", hours_needed, intensity)

        return hours_needed

    def _report_gauge(self, name, value, intensity):
        if self.report_metrics:
            metrics.gauge(f"calculator.{name}", value, tags={'intensity': intensity})

    def _needed_temperature(self, intensity: int) -> float:
        return self.config['desired_min_intensity_temperature'] + intensity / 10 * (self.config['desired_max_intensity_temperature'] - self.config['desired_min_intensity_temperature'])

    def _needed_energy(self, from_temp, to_temp):
        return 4.2 * self.config['boiler_capacity_in_liters'] * (to_temp - from_temp) / 3600

    def _sun_output(self, weather: List[WeatherData]) -> float:
        intensity = self._sun_intensity(weather)
        above_min = intensity * (self.config['sun_output_per_day_per_sq_meter_max'] - self.config['sun_output_per_day_per_sq_meter_min'])
        return (self.config['sun_output_per_day_per_sq_meter_min'] + above_min) * self.config['sun_receiving_area_in_sq_meters']

    def _sun_intensity(self, weather: List[WeatherData]) -> float:
        avg_clouds = sum(data.clouds for data in weather) / len(weather)
        avg_temp = sum(data.temperature for data in weather) / len(weather)

        if avg_temp > self.config['sun_intensity_temperature_max']:
            avg_temp = self.config['sun_intensity_temperature_max']
        if avg_temp < self.config['sun_intensity_temperature_min']:
            avg_temp = self.config['sun_intensity_temperature_min']

        temp_factor = (avg_temp - self.config['sun_intensity_temperature_min']) / (self.config['sun_intensity_temperature_max'] - self.config['sun_intensity_temperature_min'])
        clouds_factor = 1 - avg_clouds / 100
        return temp_factor * clouds_factor

    def _needed_boiler_time(self, needed_energy: float) -> float:
        boiler_output = self.config['boiler_power_in_amperes'] * self.config['voltage'] / 1000
        hours_needed = needed_energy / boiler_output
        if hours_needed < int(self.config['boiler_min_heating_time_in_minutes']) / 60:
            return 0
        return hours_needed * self.config['boiler_nurfer']