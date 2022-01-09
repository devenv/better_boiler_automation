from connectors.assistant.assistant import Assistant
from connectors.switcher.switcher import Switcher

from metrics.metrics import Metrics
from utils.logger import get_logger

logger = get_logger()
metrics = Metrics()


class BoilerController:

    def __init__(self):
        self.assistant = Assistant()
        self.switcher = Switcher()

    def is_on(self) -> bool:
        state = self.switcher.is_on()
        if state:
            metrics.gauge('boiler.boiler_on', 1)
        else:
            metrics.gauge('boiler.boiler_on', 0)
        return state

    def turn_on(self) -> None:
        self.switcher.turn_on()
        self._broadcast('Turning boiler on')
        metrics.incr('boiler.state.on')

    def turn_off(self) -> None:
        self.switcher.turn_off()
        self._broadcast('Turning boiler off')
        metrics.incr('boiler.state.off')

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