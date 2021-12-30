from unittest import TestCase
from unittest.mock import MagicMock

from datetime import datetime
from freezegun import freeze_time
from scheduler.scheduler_config import SchedulerConfig, Time

from calculator.calculator import Calculator
from scheduler.scheduler import Scheduler
from scheduler.scheduler_config import Time
from weather.weather_provider import WeatherData

from test.calculator_config_override import calculator_config_override


class TestScheduler(TestCase):

    def setUp(self):
        self.calculator = Calculator()
        self.calculator.config = calculator_config_override()

    def test_scheduler_simulation_simple(self):
        weather_data = [WeatherData(temperature=10, clouds=0)]
        times = [Time(6, 0, 10), Time(10, 0, 12)]

        boiler_controller = self._run_simulation(weather_data, times)

        self._verify_execution(boiler_controller, (4, 6), (8, 10))

    def test_scheduler_simulation_overlap(self):
        weather_data = [WeatherData(temperature=10, clouds=0)]
        times = [Time(6, 0, 10), Time(7, 0, 10)]

        boiler_controller = self._run_simulation(weather_data, times)

        self._verify_execution(boiler_controller, (4, 7))

    def test_scheduler_simulation_more_overlap(self):
        weather_data = [WeatherData(temperature=10, clouds=0)]
        times = [Time(6, 0, 10), Time(6, 30, 10), Time(7, 0, 10)]

        boiler_controller = self._run_simulation(weather_data, times)

        self._verify_execution(boiler_controller, (4, 7))

    def _datetime_for_hour(self, hour):
        return datetime(2021, 1, 1, hour, 0, 0)

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_scheduler_should_turn_on(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        self._get_scheduler(3.5, boiler_controller, [8]).check()

        self.assertEqual(boiler_controller.turned_on, 1)
        self.assertEqual(boiler_controller.turned_off, 0)

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_scheduler_should_turn_off(self):
        boiler_controller = BoilerControllerSpy(is_on=True)

        self._get_scheduler(3.5, boiler_controller, [11]).check()

        self.assertEqual(boiler_controller.turned_on, 0)
        self.assertEqual(boiler_controller.turned_off, 1)

    @freeze_time(datetime(2021, 1, 1, 23, 0, 0))
    def test_scheduler_should_turn_on_with_jump(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        self._get_scheduler(3.5, boiler_controller, [1]).check()

        self.assertEqual(boiler_controller.turned_on, 1)
        self.assertEqual(boiler_controller.turned_off, 0)

    @freeze_time(datetime(2021, 1, 1, 4, 30, 0))
    def test_find_next_schedule(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        scheduler = self._get_scheduler(3.5, boiler_controller, range(23))

        next_schedule = scheduler._get_next_schedule()
        self.assertEqual(next_schedule.hour, 5)
        self.assertEqual(next_schedule.minute, 0)

    @freeze_time(datetime(2021, 1, 1, 23, 30, 0))
    def test_find_next_schedule_warp(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        scheduler = self._get_scheduler(3.5, boiler_controller, [12, 23, 1])

        next_schedule = scheduler._get_next_schedule()
        self.assertEqual(next_schedule.hour, 1)
        self.assertEqual(next_schedule.minute, 0)

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_find_next_hour_easy(self):
        scheduler = Scheduler(None, None, None, None)
        self.assertEqual(scheduler._find_next_hour(Time(7, 30, 10)), datetime(2021, 1, 1, 7, 30, 0))

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_find_next_hour_with_jump(self):
        scheduler = Scheduler(None, None, None, None)
        self.assertEqual(scheduler._find_next_hour(Time(4, 20, 10)), datetime(2021, 1, 2, 4, 20, 0))

    def _run_simulation(self, weather_data, times):
        weather_provider = MagicMock()
        weather_provider.get_weather_data = MagicMock(return_value=weather_data)
        boiler_controller = BoilerControllerSpy(is_on=False)
        config = SchedulerConfig()
        config.times = times
        scheduler = Scheduler(weather_provider, self.calculator, boiler_controller, config)
        for i in range(24):
            with freeze_time(self._datetime_for_hour(i)):
                scheduler.check()
        return boiler_controller

    def _verify_execution(self, boiler_controller, *executions):
        self.assertEqual(boiler_controller.turned_on, len(executions))
        self.assertEqual(boiler_controller.turned_off, len(executions))
        self.assertEqual(boiler_controller.turned_on_times, [self._datetime_for_hour(n[0]) for n in executions])
        self.assertEqual(boiler_controller.turned_off_times, [self._datetime_for_hour(n[1]) for n in executions])
        
    def _get_scheduler(self, hours_to_heat, boiler_controller, configured_hours):
        self.calculator.needed_hours_to_heat = MagicMock(return_value=hours_to_heat)
        weather_provider = MagicMock()
        config = MagicMock()
        config.times = [Time(hour=hour, minute=0, intensity=0) for hour in configured_hours]
        return Scheduler(weather_provider, self.calculator, boiler_controller, config)


class BoilerControllerSpy:

    def __init__(self, is_on):
        self.turned_on = 0
        self.turned_off = 0
        self.is_onned = 0
        self._is_on = is_on
        self.turned_on_times = []
        self.turned_off_times = []

    def turn_on(self):
        self._is_on = True
        self.turned_on += 1
        self.turned_on_times.append(datetime.now())

    def turn_off(self):
        self._is_on = False
        self.turned_off += 1
        self.turned_off_times.append(datetime.now())

    def is_on(self):
        self.is_onned += 1
        return self._is_on