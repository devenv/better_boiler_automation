from dataclasses import dataclass


@dataclass
class WeatherData:
    temperature: float
    clouds: int
    feels_like: float
    visibility: int
    humidity: int
    prcipitation: int
    pressure: float
    wind_speed: int
    wind_direction: int
    solar_energy: float
    solar_radiation: float