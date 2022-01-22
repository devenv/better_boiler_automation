from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class WeatherData:
    temperature: float
    clouds: int
    feels_like: float
    visibility: int
    humidity: int
    precipitation: int
    pressure: float
    wind_speed: int
    solar_energy: float
    solar_radiation: float
    sunrise_hour: int
    sunset_hour: int