from time import sleep

from ddtrace import tracer

from boiler.boiler_controller import BoilerController, DummyBoilerController
from calculator.calculator import Calculator
from scheduler.scheduler import Scheduler
from scheduler.scheduler_config import SchedulerConfig
from weather.weather_provider import WeatherProvider

TEST_MODE = False


def main():
    with tracer.trace("main"):
        weather_provider = WeatherProvider()
        calculator = Calculator()
        if TEST_MODE:
            boiler_controller = DummyBoilerController(initial_state=False)
        else:
            boiler_controller = BoilerController()
        config = SchedulerConfig()

        scheduler = Scheduler(weather_provider, calculator, boiler_controller, config)
        scheduler.check()


if __name__ == "__main__":
    main()