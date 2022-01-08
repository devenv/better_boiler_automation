def calculator_config_override(): 
    return {
        'sun_intensity_temperature_min': 15,
        'sun_intensity_temperature_max': 30,
        'sun_output_per_day_per_sq_meter_min': 0,
        'sun_output_per_day_per_sq_meter_max': 5,
        'sun_receiving_area_in_sq_meters': 2,
        'boiler_capacity_in_liters': 100,
        'boiler_power_in_amperes': 10,
        'voltage': 220,
        'desired_max_intensity_temperature': 55,
        'desired_min_intensity_temperature': 40,
        'boiler_min_heating_time_in_minutes': 15,
        'boiler_nurfer': 1.0,
        'clouds_part': 0.2,
        'hours_ago_to_consider': 6,
    }
