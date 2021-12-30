from unittest import TestCase

from calculator.calculator import Calculator
from weather.weather_provider import WeatherData


class TestScheduler(TestCase):

    def setUp(self):
        self.calculator = Calculator()
        self.calculator.config = {
            'sun_intencity_temperature_min': 15,
            'sun_intencity_temperature_max': 30,
            'sun_output_per_day_per_sq_meter_min': 0,
            'sun_output_per_day_per_sq_meter_max': 5,
            'sun_receiving_area_in_sq_meters': 2,
            'boiler_capacity_in_liters': 100,
            'boiler_power_in_amperes': 10,
            'voltage': 220,
            'desired_max_intencity_temperature': 55,
            'desired_min_intencity_temperature': 40,
            'boiler_min_heating_time_in_minutes': 15,
            'boiler_nurfer': 1.0,
        }

    def test_needed_hours_to_heat_no_need(self):
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        hours = self.calculator.needed_hours_to_heat(weather, 10)
        self.assertEquals(hours, 0)

    def test_needed_hours_to_heat_full(self):
        weather = [
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
            WeatherData(temperature=15, clouds=100),
        ]
        hours = self.calculator.needed_hours_to_heat(weather, 10)
        self.assertAlmostEquals(hours, 2.12, places=2)

    def test_needed_hours_to_heat_full_low_intencity(self):
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

    def test_sun_intencity(self):
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        sun_intencity = self.calculator._sun_intencity(weather)
        self.assertEquals(sun_intencity, 0.5)

    def test_sun_output(self):
        weather = [
            WeatherData(temperature=29, clouds=40),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=30, clouds=50),
            WeatherData(temperature=31, clouds=60),
        ]
        sun_output = self.calculator._sun_output(weather)
        self.assertEquals(sun_output, 5)

    def test_sun_output_max(self):
        weather = [
            WeatherData(temperature=29, clouds=0),
            WeatherData(temperature=30, clouds=0),
            WeatherData(temperature=30, clouds=0),
            WeatherData(temperature=31, clouds=0),
        ]
        sun_output = self.calculator._sun_output(weather)
        self.assertEquals(sun_output, 10)

    def test_sun_output_min(self):
        weather = [
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
            WeatherData(temperature=10, clouds=0),
        ]
        sun_output = self.calculator._sun_output(weather)
        self.assertEquals(sun_output, 0)

    def test_needed_temperature(self):
        self.assertEquals(self.calculator._needed_temperature(0), 40)
        self.assertEquals(self.calculator._needed_temperature(5), 47.5)
        self.assertEquals(self.calculator._needed_temperature(10), 55)

    def test_needed_energy(self):
        needed_energy = self.calculator._needed_energy(20, 50)
        self.assertEquals(needed_energy, 3.5)

    def test_needed_boiler_time(self):
        hours = self.calculator._needed_boiler_time(5)
        self.assertAlmostEquals(hours, 2.27, places=2)

    def test_needed_boiler_time_min_hours(self):
        hours = self.calculator._needed_boiler_time(0.1)
        self.assertEquals(hours, 0)

    def test_needed_boiler_time_min_hours(self):
        hours = self.calculator._needed_boiler_time(0.1)
        self.assertEquals(hours, 0)

    def test_needed_boiler_time_with_nurfer(self):
        self.calculator.config['boiler_nurfer'] = 0.5
        hours = self.calculator._needed_boiler_time(5)
        self.assertAlmostEquals(hours, 1.135, places=2)