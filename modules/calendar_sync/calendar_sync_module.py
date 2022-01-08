from modules.module import Module
from modules.calendar_sync.calendar_sync import CalendarSync


class CalendarSyncModule(Module):

    NAME = 'calendar_sync'
    SCHEDULE = "1,6,11,16,21,26,31,36,41,46,51,56 * * * *"

    def run(self):
        super().run()
        CalendarSync().run()