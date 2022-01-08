from modules.module import Module
from modules.calendar_sync.calendar_sync import CalendarSync


class CalendarSyncModule(Module):

    NAME = 'calendar_sync'
    SCHEDULE = "0,5,10,15,20,25,30,35,40,45,50,55 * * * *"

    def run(self):
        super().run()
        CalendarSync().run()