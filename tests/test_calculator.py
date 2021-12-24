from unittest import TestCase
from unittest.mock import patch

from calculator import Calculator
from weather_provider import WeatherData


@patch('calculator.SUN_INTENCITY_TEMPERATURE_MIN', 15)
@patch('calculator.SUN_INTENCITY_TEMPERATURE_MAX', 30)
@patch('calculator.SUN_OUTPUT_PER_DAY_PER_SQ_METER_MIN', 0)
@patch('calculator.SUN_OUTPUT_PER_DAY_PER_SQ_METER_MAX', 5)
@patch('calculator.SUN_RECEIVING_AREA_IN_SQ_METERS', 2)
@patch('calculator.BOILER_CAPACITY_IN_LITERS', 100)
@patch('calculator.BOILER_POWER_IN_AMPERES', 10)
@patch('calculator.VOLTAGE', 220)
@patch('calculator.DESIRED_MAX_INTENCITY_TEMPERATURE', 55)
@patch('calculator.DESIRED_MIN_INTENCITY_TEMPERATURE', 40)
@patch('calculator.BOILER_MIN_HEATING_TIME', 0.25)
class TestScheduler(TestCase):

    def test_needed_hours_to_heat_no_need(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        hours = calculator.needed_hours_to_heat(weather, 10)
        self.assertEquals(hours, 0)

    def test_needed_hours_to_heat_full(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
        ]
        hours = calculator.needed_hours_to_heat(weather, 10)
        self.assertAlmostEquals(hours, 2.12, places=2)

    def test_needed_hours_to_heat_full_low_intencity(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
        ]
        hours = calculator.needed_hours_to_heat(weather, 0)
        self.assertAlmostEquals(hours, 1.325, places=2)

    def test_needed_hours_to_heat_some_sun(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=20, clouds=20),
            WeatherData(temperature=20, clouds=20),
            WeatherData(temperature=20, clouds=20),
            WeatherData(temperature=20, clouds=20),
        ]
        hours = calculator.needed_hours_to_heat(weather, 10)
        self.assertAlmostEquals(hours, 0.64, places=2)

    def test_sun_intencity(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        sun_intencity = calculator._sun_intencity(weather)
        self.assertEquals(sun_intencity, 0.5)

    def test_sun_output(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        sun_output = calculator._sun_output(weather)
        self.assertEquals(sun_output, 5)

    def test_sun_output_max(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=29, clouds=0),
            WeatherData(temperature=30, clouds=0),
            WeatherData(temperature=30, clouds=0),
            WeatherData(temperature=31, clouds=0),
        ]
        sun_output = calculator._sun_output(weather)
        self.assertEquals(sun_output, 10)

    def test_sun_output_min(self):
        calculator = Calculator()
        weather = [
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
        ]
        sun_output = calculator._sun_output(weather)
        self.assertEquals(sun_output, 0)

    def test_needed_temperature(self):
        calculator = Calculator()
        self.assertEquals(calculator._needed_temperature(0), 40)
        self.assertEquals(calculator._needed_temperature(5), 47.5)
        self.assertEquals(calculator._needed_temperature(10), 55)

    def test_needed_energy(self):
        calculator = Calculator()
        needed_energy = calculator._needed_energy(20, 50)
        self.assertEquals(needed_energy, 3.5)

    def test_needed_boiler_time(self):
        calculator = Calculator()
        hours = calculator._needed_boiler_time(5)
        self.assertAlmostEquals(hours, 2.27, places=2)

    def test_needed_boiler_time_min_hours(self):
        calculator = Calculator()
        hours = calculator._needed_boiler_time(0.1)
        self.assertEquals(hours, 0)