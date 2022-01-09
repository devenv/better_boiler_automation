import os
from metrics.prometheus_metrics import PrometheusMetrics
from metrics.datadog_metrics import DatadogMetrics

from utils.logger import get_logger

logger = get_logger()

STATS_ENABLED = os.environ.get('STATS_ENABLED') == 'True'
METRICS_CLIENT = 'prometheus'


class Metrics:

    def __init__(self):
        self.client = None
        if STATS_ENABLED:
            if METRICS_CLIENT.lower() == 'prometheus':
                self.client = PrometheusMetrics()
            elif METRICS_CLIENT.lower() == 'datadog':
                self.client = DatadogMetrics()

    def incr(self, metric, tags={}):
        if self.client:
            self.client.incr(metric, tags)

    def gauge(self, metric, value, tags={}):
        if self.client:
            self.client.gauge(metric, value, tags)