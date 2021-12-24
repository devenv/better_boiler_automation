from unittest import TestCase
from unittest.mock import MagicMock

from datetime import datetime
from freezegun import freeze_time

from scheduler import Scheduler
from scheduler_config import Time


class TestScheduler(TestCase):

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_scheduler_should_turn_on(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        self._get_scheduler(3.5, boiler_controller, 8).check()

        self.assertEquals(boiler_controller.turned_on, 1)
        self.assertEquals(boiler_controller.turned_off, 0)

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_scheduler_should_turn_off(self):
        boiler_controller = BoilerControllerSpy(is_on=True)

        self._get_scheduler(3.5, boiler_controller, 11).check()

        self.assertEquals(boiler_controller.turned_on, 0)
        self.assertEquals(boiler_controller.turned_off, 1)

    @freeze_time(datetime(2021, 1, 1, 23, 0, 0))
    def test_scheduler_should_turn_on_with_jump(self):
        boiler_controller = BoilerControllerSpy(is_on=False)

        self._get_scheduler(3.5, boiler_controller, 1).check()

        self.assertEquals(boiler_controller.turned_on, 1)
        self.assertEquals(boiler_controller.turned_off, 0)

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_find_next_hour_easy(self):
        scheduler = Scheduler(None, None, None, None)
        self.assertEquals(scheduler._find_next_hour(7), datetime(2021, 1, 1, 7, 0, 0))

    @freeze_time(datetime(2021, 1, 1, 5, 0, 0))
    def test_find_next_hour_with_jump(self):
        scheduler = Scheduler(None, None, None, None)
        self.assertEquals(scheduler._find_next_hour(4), datetime(2021, 1, 2, 4, 0, 0))
        
    def _get_scheduler(self, hours_to_heat, boiler_controller, configured_hour):
        calculator = MagicMock()
        calculator.needed_hours_to_heat = MagicMock(return_value=hours_to_heat)
        weather_provider = MagicMock()
        config = MagicMock()
        config.times = [Time(hour=configured_hour, minute=0, intencity=0)]
        return Scheduler(weather_provider, calculator, boiler_controller, config)


class BoilerControllerSpy:

    def __init__(self, is_on):
        self.turned_on = 0
        self.turned_off = 0
        self.is_onned = 0
        self._is_on = is_on

    def turn_on(self):
        self.turned_on += 1

    def turn_off(self):
        self.turned_off += 1

    def is_on(self):
        self.is_onned += 1
        return self._is_on