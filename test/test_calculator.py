from unittest import TestCase

from data_stores.weather.weather_data_stores import WeatherDataStore
from modules.scheduler.calculator.calculator import Calculator
from modules.scheduler.calculator.boiler import Boiler
from modules.scheduler.calculator.sun import Sun
from modules.weather.weather_data import WeatherData

from test.calculator_config_override import calculator_config_override


class TestCalculator(TestCase):

    def setUp(self):
        self.weather_ds = WeatherDataStore().clear()
        self.calculator = Calculator(self.weather_ds)
        self.calculator.config = calculator_config_override()

    def test_needed_hours_to_heat_no_need(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(29, 10), (30, 20), (30, 20), (31, 30)]))
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(10)

        self.assertEqual(hours, 0)

    def test_needed_hours_to_heat_reality_check(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.25)]))
        self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 1.729, places=2)
        self.weather_ds.clear()

        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.5)]))
        self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 1.6, places=2)
        self.weather_ds.clear()
        self.weather_ds.clear()

        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 1)]))
        self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 1.35, places=2)
        self.weather_ds.clear()

        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 2)]))
        self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 0.845, places=2)
        self.weather_ds.clear()

    def test_needed_hours_to_heat_full(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(15, 0)]))
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(10)

        self.assertAlmostEqual(hours, 2.12, places=2)

    def test_needed_hours_to_heat_full_low_intensity(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(15, 0)]))
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(0)

        self.assertAlmostEqual(hours, 1.325, places=2)

    def test_needed_hours_to_heat_some_sun(self):
        self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.5)]))
        self.calculator.load()

        hours = self.calculator.needed_hours_to_heat(10)

        self.assertAlmostEqual(hours, 1.6, places=2)

    def test_sun_output(self):
        self.assertAlmostEqual(Sun(calculator_config_override()).output(self._weather_data_with_temps_and_energies([(0, 0.25)])), 0.277, 2)

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
        self.calculator.config['boiler_nerfer'] = 0.5
        self.assertAlmostEqual(Boiler(self.calculator.config).needed_time(5), 1.136, places=2)

    def _weather_data_with_temps_and_energies(self, temps_and_energies):
        return [WeatherData(temperature, 0, 0, 0, 0, 0, 0, 0, 0, energy, 0) for temperature, energy in temps_and_energies]