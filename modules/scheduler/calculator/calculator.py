from datetime import timedelta

from data_stores.weather.weather_data_stores import WeatherDataStore
from modules.scheduler.calculator.boiler import Boiler
from modules.scheduler.calculator.clouds import Clouds
from modules.scheduler.calculator.sun import Sun

from metrics.metrics import Metrics
from utils.logger import get_logger
from utils.secrets import load_dict

logger = get_logger()
metrics = Metrics()


class Calculator:

    report_metrics: bool = False

    def __init__(self, weather_ds: WeatherDataStore, report_next_metrics: bool = False):
        self.weather_ds = weather_ds
        self.report_nex_metrics = report_next_metrics
        self.config = load_dict("calculator_config")
        self.boiler = Boiler(self.config)
        self.sun = Sun(self.config)
        
    def load(self):
        self.weather_data = self.weather_ds.read_all_values_since(timedelta(hours=self.config['hours_ago_to_consider']))
        return self

    def calculate_for_all_intensities(self):
        self.report_metrics = True
        for intensity in range(1, 11):
            self.needed_hours_to_heat(intensity)
        self.report_metrics = False

    def needed_hours_to_heat(self, intensity: int) -> float:
        self._report_gauge("intencity", intensity)
            
        avg_temp = sum(data.temperature for data in self.weather_data) / len(self.weather_data)
        self._report_gauge("avg_temp", avg_temp, intensity)

        needed_temperature = self.boiler.needed_temperature(intensity)
        self._report_gauge("needed_temperature", needed_temperature, intensity)

        needed_energy = self.boiler.needed_energy(avg_temp, needed_temperature)
        self._report_gauge("needed_energy", needed_energy, intensity)

        sun_output = self.sun.output(self.weather_data)
        logger.info(f"sun output: {sun_output}")
        self._report_gauge("sun_output", sun_output)

        delta_energy = needed_energy - sun_output
        self._report_gauge("delta_energy", delta_energy, intensity)

        if delta_energy <= 0:
            return 0

        hours_needed = self.boiler.needed_time(delta_energy)
        self._report_gauge("hours_needed", hours_needed, intensity)

        return hours_needed

    def _report_gauge(self, name, value, intensity=None):
        if self.report_metrics:
            if intensity is None:
                metrics.gauge(f"calculator.{name}", value)
            else:
                metrics.gauge(f"calculator.{name}", value, tags={'intensity': intensity})
        if self.report_nex_metrics:
            metrics.gauge(f"calculator.next_{name}", value)