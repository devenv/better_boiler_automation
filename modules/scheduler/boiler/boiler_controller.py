from connectors.ifttt.ifttt import Ifttt
from connectors.switcher.switcher import Switcher

from metrics.metrics import Metrics
from utils.logger import get_logger

logger = get_logger()
metrics = Metrics()


class BoilerController:

    def __init__(self):
        try:
            self.ifttt = Ifttt()
        except Exception:
            pass
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
        metrics.incr('boiler.state.on')
        self._broadcast('on')

    def turn_off(self) -> None:
        self.switcher.turn_off()
        metrics.incr('boiler.state.off')
        self._broadcast('off')

    def _broadcast(self, status: str) -> None:
        try:
            self.ifttt.send_json({'status': status})
        except Exception:
            pass
        logger.info(f'boiler status turned {status}')


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