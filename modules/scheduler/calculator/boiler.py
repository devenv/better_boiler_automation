class Boiler:

    def __init__(self, config):
        self.config = config

    def needed_temperature(self, intensity: int) -> float:
        return self.config['desired_min_intensity_temperature'] + intensity / 10 * (self.config['desired_max_intensity_temperature'] - self.config['desired_min_intensity_temperature'])

    def needed_energy(self, from_temp, to_temp):
        return 4.2 * self.config['boiler_capacity_in_liters'] * (to_temp - from_temp) / 3600

    def needed_time(self, needed_energy: float) -> float:
        boiler_output = self.config['boiler_power_in_amperes'] * self.config['voltage'] / 1000
        hours_needed = needed_energy / boiler_output
        if hours_needed < int(self.config['boiler_min_heating_time_in_minutes']) / 60:
            return 0
        return hours_needed * self.config['boiler_nerfer']