class Sun:

    def __init__(self, config: dict):
        self.config = config

    def output(self, temperatures) -> float:
        intensity = self.intensity(temperatures)
        above_min = intensity * (self.config['sun_output_per_day_per_sq_meter_max'] - self.config['sun_output_per_day_per_sq_meter_min'])
        return (self.config['sun_output_per_day_per_sq_meter_min'] + above_min) * self.config['sun_receiving_area_in_sq_meters']

    def intensity(self, temperatures) -> float:
        avg_temp = sum(temperature for temperature in temperatures) / len(temperatures)

        if avg_temp > self.config['sun_intensity_temperature_max']:
            avg_temp = self.config['sun_intensity_temperature_max']
        if avg_temp < self.config['sun_intensity_temperature_min']:
            avg_temp = self.config['sun_intensity_temperature_min']

        return (avg_temp - self.config['sun_intensity_temperature_min']) / (self.config['sun_intensity_temperature_max'] - self.config['sun_intensity_temperature_min'])