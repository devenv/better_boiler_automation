from datetime import datetime, timedelta
from ddtrace import tracer

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()


class Scheduler:

    def __init__(self, weather_provider, calculator, boiler_controller, config):
        self.weather_provider = weather_provider
        self.calculator = calculator
        self.boiler_controller = boiler_controller
        self.config = config

    def check(self):
        with tracer.trace("scheduler check"):
            weather = self.weather_provider.get_weather_data()
            now = datetime.now()
            is_on = self.boiler_controller.is_on()
            needs_to_be_on = False
            needs_to_be_on_time = None
            metrics.gauge("schedules loaded", len(self.config.times))
            for time in self.config.times:
                with tracer.trace("schedule calculation"):
                    hours_to_heat = self.calculator.needed_hours_to_heat(weather, time.intencity)
                    if now + timedelta(hours=hours_to_heat) >= self._find_next_hour(time.hour, time.minute):
                        needs_to_be_on = True
                        needs_to_be_on_time = time
            if not is_on and needs_to_be_on:
                logger.info(f"Switching on for hour {needs_to_be_on_time.hour + self.config.TIME_ZONE}:{needs_to_be_on_time.minute} to heat {hours_to_heat:.2f}")
                self.boiler_controller.turn_on()
            elif is_on and not needs_to_be_on:
                self.boiler_controller.turn_off()

    def _find_next_hour(self, hour: int, minute: int):
        now = datetime.now()
        if now < datetime(now.year, now.month, now.day, hour, minute, 0):
            return datetime(now.year, now.month, now.day, hour, minute, 0)
        return datetime(now.year, now.month, now.day + 1, hour, minute, 0)