from utils.logger import get_logger
from metrics.metrics import Metrics

logger = get_logger()
metrics = Metrics()


class Module:

    NAME = None
    SCHEDULE = None

    def run(self):
        logger.info(f"Running: {self.NAME}")
        metrics.incr(f"module.{self.NAME}.run")