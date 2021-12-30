from ddtrace import tracer

from assistant.assistant import Assistant

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()


class BoilerController:

    assistant = Assistant()

    def is_on(self) -> bool:
        with tracer.trace("is boiler on?"):
            _, boiler_on = self.assistant.ask('is boiler on?')
            metrics.gauge('boiler.boiler_on', 1 if boiler_on else 0)
            return boiler_on

    def turn_on(self) -> None:
        with tracer.trace("turn boiler on"):
            self.assistant.ask('turn boiler on')
            self._broadcast('Turning boiler on')
            metrics.event('boiler state', 'boiler heating', alert_type='info')
            metrics.gauge('boiler.boiler_on', 1)

    def turn_off(self) -> None:
        with tracer.trace("turn boiler off"):
            self.assistant.ask('turn boiler off')
            self._broadcast('Turning boiler off')
            metrics.event('boiler state', 'boiler off', alert_type='info')
            metrics.gauge('boiler.boiler_on', 0)

    def _broadcast(self, message: str) -> None:
        with tracer.trace("broadcast"):
            self.assistant.ask(f'broadcast "{message}"')
            logger.info(message)


class DummyBoilerController:

    assistant = Assistant()

    def __init__(self, initial_state: bool=False):
        self.test_state = initial_state

    def is_on(self) -> bool:
        return self.test_state

    def turn_on(self) -> None:
        self.test_state = True
        logger.info('Turned boiler ON')

    def turn_off(self) -> None:
        self.test_state = False
        logger.info('Turned boiler OFF')