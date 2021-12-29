from ddtrace import tracer

from logger import get_logger
from assistant.assistant import Assistant

logger = get_logger()


class BoilerController:

    assistant = Assistant()

    def is_on(self):
        with tracer.trace("is boiler on?"):
            _, lights_on = self.assistant.ask('is boiler on?')
            return lights_on

    def turn_on(self):
        with tracer.trace("turn boiler on"):
            self.assistant.ask('turn boiler on')
            self._broadcast('Boiler is on')

    def turn_off(self):
        with tracer.trace("turn boiler off"):
            self.assistant.ask('turn boiler off')
            self._broadcast('Boiler is off')

    def _broadcast(self, message):
        with tracer.trace("broadcast"):
            self.assistant.ask(f'broadcast "{message}"')
            logger.info(message)


class DummyBoilerController:

    assistant = Assistant()

    def __init__(self, initial_state=False):
        self.test_state = initial_state

    def is_on(self):
        return self.test_state

    def turn_on(self):
        self.test_state = True
        logger.info('Turned boiler ON')

    def turn_off(self):
        self.test_state = False
        logger.info('Turned boiler OFF')