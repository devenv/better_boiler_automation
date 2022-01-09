from datadog import initialize, statsd

from metrics.metrics_client import MetricsClient

from utils.logger import get_logger

logger = get_logger()


class DatadogMetrics(MetricsClient):

    options = {
        'statsd_host':'127.0.0.1',
        'statsd_port':8125
    }

    def __init__(self):
        initialize(**self.options)
        
    def incr(self, metric, amount=1, tags={}):
        statsd.increment(metric, value=amount, tags=tags)

    def gauge(self, metric, value, tags={}):
        statsd.gauge(metric, value, [f"{k}:{v}" for k, v in tags.items()])