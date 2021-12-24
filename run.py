from time import sleep
from boiler.boiler_controller import BoilerController
from calculator.calculator import Calculator
from scheduler.scheduler import Scheduler
from scheduler.scheduler_config import SchedulerConfig
from weather.weather_provider import WeatherProvider


def main():
    weather_provider = WeatherProvider()
    calculator = Calculator()
    boiler_controller = BoilerController(test_mode=True, test_state=False)
    config = SchedulerConfig()

    scheduler = Scheduler(weather_provider, calculator, boiler_controller, config)
    scheduler.check()


if __name__ == "__main__":
    while True:
        main()
        sleep(5 * 60)