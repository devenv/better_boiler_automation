from unittest import TestCase
from unittest.mock import MagicMock

from datetime import datetime
from freezegun import freeze_time

from data_stores.schedule.schedule_data_store import Time
from data_stores.weather.weather_data_stores import WeatherDataStore
from modules.calendar_sync.calendar_sync import CalendarSync
from modules.scheduler.calculator.calculator import Calculator
from modules.scheduler.scheduler import Scheduler
from modules.weather.weather_data import WeatherData

from test.calculator_config_override import calculator_config_override


class TestScheduler(TestCase):

    def setUp(self):
        self.weather_ds = WeatherDataStore().clear()
        self.calculator = Calculator(self.weather_ds)
        self.calculator.config = calculator_config_override()
        self.calculator.boiler.config = calculator_config_override()
        self.calculator.sun.config = calculator_config_override()

    def test_scheduler_simulation_simple(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(10, 0.25)]))
        self.calculator.load()
        times = [Time(6, 0, 10), Time(10, 0, 12)]

        boiler_controller = self._run_simulation(times)

        self._verify_execution(boiler_controller, (4, 6), (8, 10))

    def test_scheduler_simulation_overlap(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(10, 0.25)]))
        self.calculator.load()
        times = [Time(6, 0, 10), Time(7, 0, 10)]

        boiler_controller = self._run_simulation(times)

        self._verify_execution(boiler_controller, (4, 7))

    def test_scheduler_simulation_more_overlap(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(10, 0.25)]))
        self.calculator.load()
        times = [Time(6, 0, 10), Time(6, 30, 10), Time(7, 0, 10)]

        boiler_controller = self._run_simulation(times)

        self._verify_execution(boiler_controller, (4, 7))

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_scheduler_should_turn_on(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        self._get_scheduler(3.5, boiler_controller, [8]).run()

        self.assertEqual(boiler_controller.turned_on, 1)
        self.assertEqual(boiler_controller.turned_off, 0)

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_scheduler_should_turn_off(self):
        boiler_controller = BoilerControllerSpy(is_on=True)

        self._get_scheduler(3.5, boiler_controller, [11]).run()

        self.assertEqual(boiler_controller.turned_on, 0)
        self.assertEqual(boiler_controller.turned_off, 1)

    @freeze_time(datetime(2021, 1, 1, 23, 0, 0))
    def test_scheduler_should_turn_on_with_jump(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        self._get_scheduler(3.5, boiler_controller, [1]).run()

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
        scheduler = self._get_scheduler(3.5, None, [12, 23, 1])
        self.assertEqual(scheduler._find_next_hour(Time(7, 30, 10)), datetime(2021, 1, 1, 7, 30, 0))

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_find_next_hour_with_jump(self):
        scheduler = self._get_scheduler(3.5, None, [12, 23, 1])
        self.assertEqual(scheduler._find_next_hour(Time(4, 20, 10)), datetime(2021, 1, 2, 4, 20, 0))
    
    def test_calendar_sync_output_format(self):
        magic_start = MagicMock()
        magic_start.get = MagicMock(return_value='2022-01-01T08:30:00.000000')
        events = [{
            'start': magic_start,
            'summary': 'Boiler intensity:10',
        }]
        result = CalendarSync().get_schedule(events)
        self.assertEqual(result, [Time(8, 30, 10)])

    def _run_simulation(self, times):
        boiler_controller = BoilerControllerSpy(is_on=False)
        scheduler = Scheduler(times, self.calculator, boiler_controller)
        for i in range(24):
            with freeze_time(self._datetime_for_hour(i)):
                scheduler.run()
        return boiler_controller

    def _verify_execution(self, boiler_controller, *executions):
        self.assertEqual(boiler_controller.turned_on, len(executions))
        self.assertEqual(boiler_controller.turned_off, len(executions))
        self.assertEqual(boiler_controller.turned_on_times, [self._datetime_for_hour(n[0]) for n in executions])
        self.assertEqual(boiler_controller.turned_off_times, [self._datetime_for_hour(n[1]) for n in executions])

    def _datetime_for_hour(self, hour):
        return datetime(2021, 1, 1, hour, 0, 0)
        
    def _get_scheduler(self, hours_to_heat, boiler_controller, configured_hours):
        self.calculator.needed_hours_to_heat = MagicMock(return_value=hours_to_heat)
        times = [Time(hour=hour, minute=0, intensity=0) for hour in configured_hours]
        return Scheduler(times, self.calculator, boiler_controller)

    def _weather_data_with_temps_and_energies(self, temps_and_energies):
        return [WeatherData(12, temperature, 0, 0, 0, 0, 0, 0, 0, energy / 3600, 0, 10, 14) for temperature, energy in temps_and_energies]


class BoilerControllerSpy:

    def __init__(self, is_on=False):
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