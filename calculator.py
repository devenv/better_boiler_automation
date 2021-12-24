
SUN_INTENCITY_TEMPERATURE_MIN = 15
SUN_INTENCITY_TEMPERATURE_MAX = 35

SUN_OUTPUT_PER_DAY_PER_SQ_METER_MIN = 0
SUN_OUTPUT_PER_DAY_PER_SQ_METER_MAX = 5
SUN_RECEIVING_AREA_IN_SQ_METERS = 2

BOILER_CAPACITY_IN_LITERS = 100
BOILER_POWER_IN_AMPERES = 10
VOLTAGE = 220
BOILER_MIN_HEATING_TIME = 0.25

DESIRED_MAX_INTENCITY_TEMPERATURE = 55
DESIRED_MIN_INTENCITY_TEMPERATURE = 40

class Calculator:

    def needed_hours_to_heat(self, weather, intencity):
        avg_temp = sum(data.temperature for data in weather) / len(weather)
        needed_temperature = self._needed_temperature(intencity)
        needed_energy = self._needed_energy(avg_temp, needed_temperature)
        delta_energy = needed_energy - self._sun_output(weather)
        if delta_energy <= 0:
            return 0
        hours_needed = self._needed_boiler_time(delta_energy)
        print(f"Hours needed to heat to intencity {intencity}: {hours_needed}")
        return hours_needed

    def _sun_output(self, weather):
        intencity = self._sun_intencity(weather)
        above_min = intencity * (SUN_OUTPUT_PER_DAY_PER_SQ_METER_MAX - SUN_OUTPUT_PER_DAY_PER_SQ_METER_MIN)
        return (SUN_OUTPUT_PER_DAY_PER_SQ_METER_MIN + above_min) * SUN_RECEIVING_AREA_IN_SQ_METERS

    def _sun_intencity(self, weather):
        avg_clouds = sum(data.clouds for data in weather) / len(weather)
        avg_temp = sum(data.temperature for data in weather) / len(weather)
        if avg_temp > SUN_INTENCITY_TEMPERATURE_MAX:
            avg_temp = SUN_INTENCITY_TEMPERATURE_MAX
        if avg_temp < SUN_INTENCITY_TEMPERATURE_MIN:
            avg_temp = SUN_INTENCITY_TEMPERATURE_MIN
        temp_factor = (avg_temp - SUN_INTENCITY_TEMPERATURE_MIN) / (SUN_INTENCITY_TEMPERATURE_MAX - SUN_INTENCITY_TEMPERATURE_MIN)
        clouds_factor = 1 - avg_clouds / 100
        return temp_factor * clouds_factor

    def _needed_energy(self, from_temp, to_temp):
        return 4.2 * BOILER_CAPACITY_IN_LITERS * (to_temp - from_temp) / 3600

    def _needed_temperature(self, intencity):
        return DESIRED_MIN_INTENCITY_TEMPERATURE + intencity / 10 * (DESIRED_MAX_INTENCITY_TEMPERATURE - DESIRED_MIN_INTENCITY_TEMPERATURE)

    def _needed_boiler_time(self, needed_energy):
        boiler_output = BOILER_POWER_IN_AMPERES * VOLTAGE / 1000
        hours_needed = needed_energy / boiler_output
        if hours_needed < BOILER_MIN_HEATING_TIME:
            return 0
        return hours_needed