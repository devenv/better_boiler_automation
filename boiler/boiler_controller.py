from ddtrace import tracer

from assistant.assistant import Assistant

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()


class BoilerController:

    assistant = Assistant()

    def is_on(self):
        with tracer.trace("is boiler on?"):
            _, boiler_on = self.assistant.ask('is boiler on?')
            metrics.gauge('boiler_on', 1 if boiler_on else 0)
            return boiler_on

    def turn_on(self):
        with tracer.trace("turn boiler on"):
            self.assistant.ask('turn boiler on')
            self._broadcast('Boiler is on')
            metrics.event('boiler state', 'boiler heating', alert_type='info')

    def turn_off(self):
        with tracer.trace("turn boiler off"):
            self.assistant.ask('turn boiler off')
            self._broadcast('Boiler is off')
            metrics.event('boiler state', 'boiler off', alert_type='info')

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