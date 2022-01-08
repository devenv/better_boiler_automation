from data_stores.weather.weather_data_stores import CloudsDataStore, TemperatureDataStore
from modules.scheduler.calculator.boiler import Boiler
from modules.scheduler.calculator.clouds import Clouds
from modules.scheduler.calculator.sun import Sun

from utils.logger import get_logger
from utils.metrics import Metrics
from utils.secrets import load_dict

logger = get_logger()
metrics = Metrics()


class Calculator:

    report_metrics: bool = False

    def __init__(self, temperature_ds: TemperatureDataStore, clouds_ds: CloudsDataStore):
        self.temperature_ds = temperature_ds
        self.clouds_ds = clouds_ds
        self.config = load_dict("calculator_config")
        
    def load(self):
        self.temperatures = self.temperature_ds.read_all_values()
        self.clouds = self.clouds_ds.read_all_values()

    def calculate_for_all_intensities(self):
        self.report_metrics = True
        for intensity in range(4, 10):
            self.needed_hours_to_heat(intensity)
        self.report_metrics = False

    def needed_hours_to_heat(self, intensity: int) -> float:
        avg_temp = sum(temperature for temperature in self.temperatures) / len(self.temperatures)
        self._report_gauge("avg_temp", avg_temp, intensity)

        boiler = Boiler(self.config)
        needed_temperature = boiler.needed_temperature(intensity)
        self._report_gauge("needed_temperature", needed_temperature, intensity)

        needed_energy = boiler.needed_energy(avg_temp, needed_temperature)
        self._report_gauge("needed_energy", needed_energy, intensity)

        sun_output = Sun(self.config).output(self.temperatures)
        self._report_gauge("sun_output", sun_output)
        cloudiness = Clouds(self.config).cloudiness(self.clouds)
        self._report_gauge("clouds_factor", cloudiness)
        sun_output = (sun_output * (1 - self.config['clouds_part'])) + (cloudiness * self.config['clouds_part'])
        self._report_gauge("sun_output_with_clouds", sun_output)

        delta_energy = needed_energy - sun_output
        self._report_gauge("delta_energy", delta_energy, intensity)

        if delta_energy <= 0:
            return 0

        hours_needed = boiler.needed_time(delta_energy)
        self._report_gauge("hours_needed", hours_needed, intensity)

        return hours_needed

    def _report_gauge(self, name, value, intensity=None):
        if self.report_metrics:
            if intensity is None:
                metrics.gauge(f"calculator.{name}", value)
            else:
                metrics.gauge(f"calculator.{name}", value, tags={'intensity': intensity})