from modules.calendar_sync.calendar_sync_module import CalendarSyncModule
from modules.weather.weather_module import WeatherModule
from modules.scheduler.scheduler_module import SchedulerModule

available_modules = [CalendarSyncModule, WeatherModule, SchedulerModule]
modules_by_name = {module.NAME: module for module in available_modules}