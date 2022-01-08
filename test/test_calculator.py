from unittest import TestCase

from data_stores.weather.weather_data_stores import CloudsDataStore, TemperatureDataStore
from modules.scheduler.calculator.calculator import Calculator
from modules.scheduler.calculator.boiler import Boiler
from modules.scheduler.calculator.sun import Sun
from modules.weather.weather_provider import WeatherData

from test.calculator_config_override import calculator_config_override


class TestCalculator(TestCase):

    def setUp(self):
        self.temperature_ds = TemperatureDataStore().clear()
        self.clouds_ds = CloudsDataStore().clear()
        self.calculator = Calculator(self.temperature_ds, self.clouds_ds)
        self.calculator.config = calculator_config_override()

    def test_needed_hours_to_heat_no_need(self):
        self.temperature_ds.add_values([29, 30, 30, 31])
        self.clouds_ds.add_values([40, 50, 50, 60])
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(10)

        self.assertEqual(hours, 0)

    def test_needed_hours_to_heat_full(self):
        self.temperature_ds.add_values([15])
        self.clouds_ds.add_values([100])
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(10)

        self.assertAlmostEqual(hours, 2.12, places=2)

    def test_needed_hours_to_heat_full_low_intensity(self):
        self.temperature_ds.add_values([15])
        self.clouds_ds.add_values([100])
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(0)

        self.assertAlmostEqual(hours, 1.325, places=2)

    def test_needed_hours_to_heat_some_sun(self):
        self.temperature_ds.add_values([20])
        self.clouds_ds.add_values([20])
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(10)

        self.assertAlmostEqual(hours, 0.40, places=2)

    def test_sun_intensity(self):
        self.assertEqual(Sun(self.calculator.config).intensity([21]), 0.4)

    def test_sun_output(self):
        self.assertEqual(Sun(self.calculator.config).output([21]), 4.0)

    def test_sun_output_max(self):
        self.assertEqual(Sun(self.calculator.config).output([50]), 10.0)

    def test_sun_output_min(self):
        self.assertEqual(Sun(self.calculator.config).output([10]), 0)

    def test_needed_temperature(self):
        boiler = Boiler(self.calculator.config)
        self.assertEqual(boiler.needed_temperature(0), 40)
        self.assertEqual(boiler.needed_temperature(5), 47.5)
        self.assertEqual(boiler.needed_temperature(10), 55)

    def test_needed_energy(self):
        self.assertEqual(Boiler(self.calculator.config).needed_energy(20, 50), 3.5)

    def test_needed_boiler_time(self):
        self.assertAlmostEqual(Boiler(self.calculator.config).needed_time(5), 2.27, places=2)

    def test_needed_boiler_time_min_hours(self):
        self.assertEqual(Boiler(self.calculator.config).needed_time(0.1), 0)

    def test_needed_boiler_time_with_nurfer(self):
        self.calculator.config['boiler_nurfer'] = 0.5
        self.assertAlmostEqual(Boiler(self.calculator.config).needed_time(5), 1.136, places=2)

    def test_clouds_part(self):
        self.temperature_ds.add_values([20])
        self.clouds_ds.add_values([50])
        self.calculator.load()

        self.calculator.config['clouds_part'] = 0
        hours = self.calculator.needed_hours_to_heat(10)
        self.assertAlmostEqual(hours, 0.34, places=2)
        
        self.calculator.config['clouds_part'] = 1
        hours = self.calculator.needed_hours_to_heat(10)
        self.assertAlmostEqual(hours, 1.098, places=2)

        self.calculator.config['clouds_part'] = 0.5
        hours = self.calculator.needed_hours_to_heat(10)
        self.assertAlmostEqual(hours, 0.719, places=2)