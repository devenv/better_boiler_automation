import random

from assistant import Assistant


class BoilerController:

    assistant = Assistant()

    def __init__(self, test_mode=False, test_state=False):
        self.test_mode = test_mode
        self.test_state = test_state

    def is_on(self):
        if self.test_mode:
            return self.test_state
        return self.assistant.is_boiler_on()

    def turn_on(self):
        if self.test_mode:
            self.test_state = True
            print('Turned boiler ON')
            return True
        self.assistant.boiler_on()

    def turn_off(self):
        if self.test_mode:
            self.test_state = False
            print('Turned boiler OFF')
            return True
        self.assistant.boiler_off()