import __main__
import os
from typing import Dict
from prometheus_client import CollectorRegistry, Gauge, Counter, write_to_textfile

from metrics.metrics_client import MetricsClient

JOB_NAME = __main__.__file__
GLOBAL_STORE = os.environ.get("GLOBAL_STORE") == 'True'
if GLOBAL_STORE:
    METRICS_FILE = f"{os.path.expanduser('~')}/.boiler/data/metrics.txt"
else:
    METRICS_FILE = "data/metrics.txt"


class PrometheusMetrics(MetricsClient):

    def incr(self, metric: str, tags: Dict[str, str] = {}):
        registry = CollectorRegistry()
        metric = metric.replace('.', '_')
        counter = Counter(metric, metric, labelnames=list(tags.keys()), registry=registry)
        if tags:
            counter = counter.labels(tags)
        counter.inc()
        write_to_textfile(METRICS_FILE, registry)

    def gauge(self, metric: str, value: float, tags: Dict[str, str] = {}):
        registry = CollectorRegistry()
        gauge = Gauge(metric, metric, labelnames=list(tags.keys()), registry=registry)
        if tags:
            gauge = gauge.labels(tags)
        gauge.set(value)
        write_to_textfile(METRICS_FILE, registry)