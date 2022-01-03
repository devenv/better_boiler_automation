from datetime import datetime, timedelta
from ddtrace import tracer
from typing import List

from boiler.boiler_controller import BoilerController
from calculator.calculator import Calculator
from scheduler.scheduler_config import SchedulerConfig, Time
from weather.weather_provider import WeatherProvider, WeatherData

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()


class Scheduler:

    def __init__(self, weather_provider: WeatherProvider, calculator: Calculator, boiler_controller: BoilerController, config: SchedulerConfig):
        self.weather_provider = weather_provider
        self.calculator = calculator
        self.boiler_controller = boiler_controller
        self.config = config

    def check(self) -> None:
        metrics.gauge("scheduler.schedules_loaded", len(self.config.times))
        with tracer.trace("scheduler check"):
            now = datetime.now()
            weather: List[WeatherData] = self.weather_provider.get_weather_data()
            is_on = self.boiler_controller.is_on()

            with tracer.trace("schedule calculation"):

                self.calculator.calculate_for_all_intensities(weather)

                time = self._get_next_schedule()
                metrics.gauge("scheduler.next_schedule", self.config.cull_to_real_hour(time.hour + self.config.TIME_ZONE) + time.minute / 60, tags={'intensity': time.intensity})
                metrics.gauge("scheduler.next_intensity", time.intensity, tags={'intensity': time.intensity})
                metrics.gauge("scheduler.next_temperature", self.calculator._needed_temperature(time.intensity), tags={'intensity': time.intensity})

                hours_to_heat = self.calculator.needed_hours_to_heat(weather, time.intensity)
                metrics.gauge("scheduler.next_hours_needed", hours_to_heat, tags={'intensity': time.intensity})

                eta_on = 0 if is_on else (self._find_next_hour(time) - timedelta(hours=hours_to_heat) - now).seconds / 60 / 60
                eta_off = (self._find_next_hour(time) - now).seconds / 60 / 60
                metrics.gauge("scheduler.eta_on", eta_on, tags={'intensity': time.intensity})
                metrics.gauge("scheduler.eta_off", eta_off, tags={'intensity': time.intensity})

                if now + timedelta(hours=hours_to_heat) >= self._find_next_hour(time):
                    if not is_on:
                        logger.info(f"Switching on for hour {self.config.cull_to_real_hour(time.hour + self.config.TIME_ZONE)}:{time.minute} to heat {hours_to_heat:.2f}")
                        metrics.gauge("scheduler.hours_heating", hours_to_heat, tags={'intensity': time.intensity})
                        self.boiler_controller.turn_on()
                elif is_on:
                    self.boiler_controller.turn_off()

    def _get_next_schedule(self) -> Time:
        now = datetime.now()
        minimal_time = self.config.times[0]
        for time in self.config.times:
            next_time = self._find_next_hour(time)
            if next_time - now < self._find_next_hour(minimal_time) - now:
                minimal_time = time
        return minimal_time

    def _find_next_hour(self, time: Time) -> datetime:
        now = datetime.now()
        if now < datetime(now.year, now.month, now.day, time.hour, time.minute, 0):
            return datetime(now.year, now.month, now.day, time.hour, time.minute, 0)
        tomorrow = datetime.now() + timedelta(days=1)
        return datetime(tomorrow.year, tomorrow.month, tomorrow.day, time.hour, time.minute, 0)