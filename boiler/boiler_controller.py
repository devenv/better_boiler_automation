from logger import get_logger

from assistant.assistant import Assistant

logger = get_logger()


class BoilerController:

    assistant = Assistant()

    def __init__(self, test_mode=False, test_state=False):
        self.test_mode = test_mode
        self.test_state = test_state

    def is_on(self):
        if self.test_mode:
            return self.test_state
        _, lights_on = self.assistant.ask('are lights on?')
        return lights_on

    def turn_on(self):
        if self.test_mode:
            self.test_state = True
            logger.info('Turned boiler ON')
            return True
        self.assistant.ask('turn lights on')
        self._broadcast('boiler is on')

    def turn_off(self):
        if self.test_mode:
            self.test_state = False
            logger.info('Turned boiler OFF')
            return True
        self.assistant.ask('turn lights off')
        self._broadcast('boiler is off')

    def _broadcast(self, message):
        self.assistant.ask(f'broadcast "{message}"')