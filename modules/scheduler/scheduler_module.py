from modules.module import Module
from data_stores.weather.weather_data_stores import CloudsDataStore, TemperatureDataStore
from data_stores.schedule.schedule_data_store import ScheduleDataStore
from modules.scheduler.boiler.boiler_controller import BoilerController, DummyBoilerController
from modules.scheduler.calculator.calculator import Calculator
from modules.scheduler.scheduler import Scheduler


class SchedulerModule(Module):

    TEST_MODE = False
    NAME = 'scheduler'
    SCHEDULE = "2,7,12,17,22,27,32,37,42,47,52,57 * * * *"

    def run(self):
        super().run()
        calculator = Calculator(TemperatureDataStore(), CloudsDataStore()).load()
        schedule = ScheduleDataStore().load_schedule()
        if self.TEST_MODE:
            boiler_controller = DummyBoilerController(initial_state=False)
        else:
            boiler_controller = BoilerController()
        scheduler = Scheduler(schedule, calculator, boiler_controller)
        scheduler.run()