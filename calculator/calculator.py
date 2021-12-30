import json
import os
import sys

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()

def load_config():
    with open(os.path.join(sys.path[0], "calculator/calculator_config.json"), "r") as f:
        return json.load(f)


class Calculator:

    config = load_config()

    def needed_hours_to_heat(self, weather, intencity):
        avg_temp = sum(data.temperature for data in weather) / len(weather)
        metrics.gauge("calculator.avg_temp", avg_temp, tags={'intencity': intencity})
        needed_temperature = self._needed_temperature(intencity)
        metrics.gauge("calculator.needed_temperature", needed_temperature, tags={'intencity': intencity})
        needed_energy = self._needed_energy(avg_temp, needed_temperature)
        metrics.gauge("calculator.needed_energy", needed_energy, tags={'intencity': intencity})
        delta_energy = needed_energy - self._sun_output(weather)
        metrics.gauge("calculator.delta_energy", delta_energy, tags={'intencity': intencity})
        if delta_energy <= 0:
            return 0
        hours_needed = self._needed_boiler_time(delta_energy)
        metrics.gauge("calculator.hours_needed", hours_needed, tags={'intencity': intencity})
        logger.info(f"Hours needed to heat to intencity {intencity}: {hours_needed:.2f}h")
        return hours_needed

    def _needed_temperature(self, intencity):
        return self.config['desired_min_intencity_temperature'] + intencity / 10 * (self.config['desired_max_intencity_temperature'] - self.config['desired_min_intencity_temperature'])

    def _needed_energy(self, from_temp, to_temp):
        return 4.2 * self.config['boiler_capacity_in_liters'] * (to_temp - from_temp) / 3600

    def _sun_output(self, weather):
        intencity = self._sun_intencity(weather)
        above_min = intencity * (self.config['sun_output_per_day_per_sq_meter_max'] - self.config['sun_output_per_day_per_sq_meter_min'])
        return (self.config['sun_output_per_day_per_sq_meter_min'] + above_min) * self.config['sun_receiving_area_in_sq_meters']

    def _sun_intencity(self, weather):
        avg_clouds = sum(data.clouds for data in weather) / len(weather)
        avg_temp = sum(data.temperature for data in weather) / len(weather)
        if avg_temp > self.config['sun_intencity_temperature_max']:
            avg_temp = self.config['sun_intencity_temperature_max']
        if avg_temp < self.config['sun_intencity_temperature_min']:
            avg_temp = self.config['sun_intencity_temperature_min']
        temp_factor = (avg_temp - self.config['sun_intencity_temperature_min']) / (self.config['sun_intencity_temperature_max'] - self.config['sun_intencity_temperature_min'])
        clouds_factor = 1 - avg_clouds / 100
        return temp_factor * clouds_factor

    def _needed_boiler_time(self, needed_energy):
        boiler_output = self.config['boiler_power_in_amperes'] * self.config['voltage'] / 1000
        hours_needed = needed_energy / boiler_output
        if hours_needed < int(self.config['boiler_min_heating_time_in_minutes']) / 60:
            return 0
        return hours_needed * self.config['boiler_nurfer']