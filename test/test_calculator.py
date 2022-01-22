from unittest import TestCase

from datetime import datetime
from freezegun import freeze_time

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
        self.calculator.sun.config = calculator_config_override()
        self.calculator.boiler.config = calculator_config_override()

    def test_needed_hours_to_heat_no_need(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(29, 10), (30, 20), (30, 20), (31, 30)]))
            self.calculator.load()

            hours = self.calculator.needed_hours_to_heat(10)

            self.assertEqual(hours, 0)

    def test_needed_hours_to_heat_reality_check(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.07)]))
            self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 1.728 , places=2)
            self.weather_ds.clear()

            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.14)]))
            self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 1.602, places=2)
            self.weather_ds.clear()
            self.weather_ds.clear()

            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.28)]))
            self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 1.347, places=2)
            self.weather_ds.clear()

            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.56)]))
            self.assertAlmostEqual(self.calculator.load().needed_hours_to_heat(10), 0.838, places=2)
            self.weather_ds.clear()

    def test_needed_hours_to_heat_full(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(15, 0)]))
            self.calculator.load()

            hours = self.calculator.needed_hours_to_heat(10)

            self.assertAlmostEqual(hours, 2.12, places=2)

    def test_needed_hours_to_heat_full_low_intensity(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(15, 0)]))
            self.calculator.load()

            hours = self.calculator.needed_hours_to_heat(0)

            self.assertAlmostEqual(hours, 1.325, places=2)

    def test_needed_hours_to_heat_some_sun(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.weather_ds.add_values(self._weather_data_with_temps_and_energies([(20, 0.139)]))
            self.calculator.load()

            hours = self.calculator.needed_hours_to_heat(10)

            self.assertAlmostEqual(hours, 1.603, places=2)

    def test_needed_temperature(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            boiler = Boiler(self.calculator.config)
            self.assertEqual(boiler.needed_temperature(0), 40)
            self.assertEqual(boiler.needed_temperature(5), 47.5)
            self.assertEqual(boiler.needed_temperature(10), 55)

    def test_needed_energy(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.assertEqual(Boiler(self.calculator.config).needed_energy(20, 50), 3.5)

    def test_needed_boiler_time(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.assertAlmostEqual(Boiler(self.calculator.config).needed_time(5), 2.27, places=2)

    def test_needed_boiler_time_min_hours(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.assertEqual(Boiler(self.calculator.config).needed_time(0.1), 0)

    def test_needed_boiler_time_with_nurfer(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.calculator.config['boiler_nerfer'] = 0.5
            self.assertAlmostEqual(Boiler(self.calculator.config).needed_time(5), 1.136, places=2)

    def test_sun_output(self):
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.assertAlmostEqual(Sun(calculator_config_override()).output(self._weather_data_with_temps_and_energies([(0, 0.07)])), 0.28, 2)

    def test_sun_angle_full(self):
        weather_data = self._weather_data_with_temps_and_energies([(0, 0.07)])
        weather_data[0].sunrise_hour = 10
        weather_data[0].sunset_hour = 14
        with freeze_time(datetime(2021, 1, 1, 12, 0, 0)):
            self.assertAlmostEqual(Sun(calculator_config_override()).output(weather_data), 0.28, 2)

    def test_sun_angle_some(self):
        weather_data = self._weather_data_with_temps_and_energies([(0, 0.07)])
        weather_data[0].sunrise_hour = 10
        weather_data[0].sunset_hour = 14
        with freeze_time(datetime(2021, 1, 1, 11, 0, 0)):
            self.assertAlmostEqual(Sun(calculator_config_override()).output(weather_data), 0.14, 2)

    def test_sun_angle_none(self):
        weather_data = self._weather_data_with_temps_and_energies([(0, 0.07)])
        weather_data[0].sunrise_hour = 10
        weather_data[0].sunset_hour = 14
        with freeze_time(datetime(2021, 1, 1, 10, 0, 0)):
            self.assertEqual(Sun(calculator_config_override()).output(weather_data), 0)

    def _weather_data_with_temps_and_energies(self, temps_and_energies):
        return [WeatherData(temperature, 0, 0, 0, 0, 0, 0, 0, energy, 0, 6, 18) for temperature, energy in temps_and_energies]