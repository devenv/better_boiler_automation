from modules.module import Module
from modules.calendar_sync.calendar_sync import CalendarSync


class CalendarSyncModule(Module):

    NAME = 'calendar_sync'
    SCHEDULE = "*/5 * * * *"

    def run(self):
        CalendarSync().run()