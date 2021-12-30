from unittest import TestCase

from calculator.calculator import Calculator
from weather.weather_provider import WeatherData

from test.calculator_config_override import calculator_config_override


class TestScheduler(TestCase):

    def setUp(self):
        self.calculator = Calculator()
        self.calculator.config = calculator_config_override()

    def test_needed_hours_to_heat_no_need(self):
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        hours = self.calculator.needed_hours_to_heat(weather, 10)
        self.assertEqual(hours, 0)

    def test_needed_hours_to_heat_full(self):
        weather = [
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
        ]
        self.calculator.stop = True
        hours = self.calculator.needed_hours_to_heat(weather, 10)
        self.assertAlmostEquals(hours, 2.12, places=2)

    def test_needed_hours_to_heat_full_low_intensity(self):
        weather = [
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
        ]
        hours = self.calculator.needed_hours_to_heat(weather, 0)
        self.assertAlmostEquals(hours, 1.325, places=2)

    def test_needed_hours_to_heat_some_sun(self):
        weather = [
            WeatherData(temperature=20, clouds=20),
            WeatherData(temperature=20, clouds=20),
            WeatherData(temperature=20, clouds=20),
            WeatherData(temperature=20, clouds=20),
        ]
        hours = self.calculator.needed_hours_to_heat(weather, 10)
        self.assertAlmostEquals(hours, 0.64, places=2)

    def test_sun_intensity(self):
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        sun_intensity = self.calculator._sun_intensity(weather)
        self.assertEqual(sun_intensity, 0.5)

    def test_sun_output(self):
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        sun_output = self.calculator._sun_output(weather)
        self.assertEqual(sun_output, 5)

    def test_sun_output_max(self):
        weather = [
            WeatherData(temperature=29, clouds=0),
            WeatherData(temperature=30, clouds=0),
            WeatherData(temperature=30, clouds=0),
            WeatherData(temperature=31, clouds=0),
        ]
        sun_output = self.calculator._sun_output(weather)
        self.assertEqual(sun_output, 10)

    def test_sun_output_min(self):
        weather = [
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
        ]
        sun_output = self.calculator._sun_output(weather)
        self.assertEqual(sun_output, 0)

    def test_needed_temperature(self):
        self.assertEqual(self.calculator._needed_temperature(0), 40)
        self.assertEqual(self.calculator._needed_temperature(5), 47.5)
        self.assertEqual(self.calculator._needed_temperature(10), 55)

    def test_needed_energy(self):
        needed_energy = self.calculator._needed_energy(20, 50)
        self.assertEqual(needed_energy, 3.5)

    def test_needed_boiler_time(self):
        hours = self.calculator._needed_boiler_time(5)
        self.assertAlmostEquals(hours, 2.27, places=2)

    def test_needed_boiler_time_min_hours(self):
        hours = self.calculator._needed_boiler_time(0.1)
        self.assertEqual(hours, 0)

    def test_needed_boiler_time_min_hours(self):
        hours = self.calculator._needed_boiler_time(0.1)
        self.assertEqual(hours, 0)

    def test_needed_boiler_time_with_nurfer(self):
        self.calculator.config['boiler_nurfer'] = 0.5
        hours = self.calculator._needed_boiler_time(5)
        self.assertAlmostEquals(hours, 1.135, places=2)