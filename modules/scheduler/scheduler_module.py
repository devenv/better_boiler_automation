from datetime import timedelta

from data_stores.schedule.schedule_data_store import ScheduleDataStore
from data_stores.weather.weather_data_stores import WeatherDataStore
from modules.calendar_sync.calendar_sync import TIME_ZONE
from modules.module import Module
from modules.scheduler.boiler.boiler_controller import BoilerController, DummyBoilerController
from modules.scheduler.calculator.calculator import Calculator
from modules.scheduler.scheduler import Scheduler

from utils.logger import get_logger
from utils.secrets import load_dict

logger = get_logger()


class SchedulerModule(Module):

    TEST_MODE = False
    NAME = 'scheduler'
    SCHEDULE = "4,9,14,19,24,29,34,39,44,49,54,59 * * * *"

    def run(self):
        super().run()

        config = load_dict("calculator_config")
    
        calculator = Calculator(WeatherDataStore(freshness=timedelta(hours=config['hours_ago_to_consider'])), report_next_metrics=True).load()
        schedule = ScheduleDataStore().load_schedule()
        schedule = [time.plus_hours(0 - TIME_ZONE) for time in schedule]
        logger.info(f"Got schedule: {schedule}")
        if self.TEST_MODE:
            boiler_controller = DummyBoilerController(initial_state=False)
        else:
            boiler_controller = BoilerController()
        scheduler = Scheduler(schedule, calculator, boiler_controller)
        scheduler.run()