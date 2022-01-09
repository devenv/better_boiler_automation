import __main__
import os
from typing import Dict
from prometheus_client import CollectorRegistry, Gauge, Counter, write_to_textfile

from metrics.metrics_client import MetricsClient

JOB_NAME = __main__.__file__
GLOBAL_STORE = os.environ.get("GLOBAL_STORE") == 'True'
if GLOBAL_STORE:
    METRICS_FILE = f"{os.path.expanduser('~')}/.boiler/data/{JOB_NAME.replace('/', '_')}_metrics.prom"
else:
    METRICS_FILE = "data/metrics.txt"

registry = CollectorRegistry()

class PrometheusMetrics(MetricsClient):

    def incr(self, metric: str, tags: Dict[str, str] = {}):
        metric = metric.replace('.', '_')
        if metric in registry._names_to_collectors:
            counter = registry._names_to_collectors[metric]
        else:
            counter = Counter(metric, metric, labelnames=list(tags.keys()), registry=registry)
        if tags:
            counter = counter.labels(tags)
        counter.inc()
        write_to_textfile(METRICS_FILE, registry)

    def gauge(self, metric: str, value: float, tags: Dict[str, str] = {}):
        metric = metric.replace('.', '_')
        if metric in registry._names_to_collectors:
            gauge = registry._names_to_collectors[metric]
        else:
            gauge = Gauge(metric, metric, labelnames=list(tags.keys()), registry=registry)
        if tags:
            gauge = gauge.labels(tags)
        gauge.set(value)
        write_to_textfile(METRICS_FILE, registry)