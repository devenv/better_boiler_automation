from assistant.assistant import Assistant
from switcher.switcher import Switcher

from logger import get_logger
from metrics import Metrics

logger = get_logger()
metrics = Metrics()


class BoilerController:

    assistant = Assistant()
    switcher = Switcher()

    def is_on(self) -> bool:
        return self.switcher.is_on()

    def turn_on(self) -> None:
        self.switcher.turn_off()
        self._broadcast('Turning boiler on')
        metrics.event('boiler state', 'boiler heating', alert_type='info')
        metrics.gauge('boiler.boiler_on', 1)

    def turn_off(self) -> None:
        self.switcher.turn_off()
        self._broadcast('Turning boiler off')
        metrics.event('boiler state', 'boiler off', alert_type='info')
        metrics.gauge('boiler.boiler_on', 0)

    def _broadcast(self, message: str) -> None:
        self.assistant.ask(f'broadcast "{message}"')
        logger.info(message)


class DummyBoilerController:

    def __init__(self, initial_state: bool = False):
        self.test_state = initial_state

    def is_on(self) -> bool:
        return self.test_state

    def turn_on(self) -> None:
        self.test_state = True
        logger.info('Turned boiler ON')

    def turn_off(self) -> None:
        self.test_state = False
        logger.info('Turned boiler OFF')