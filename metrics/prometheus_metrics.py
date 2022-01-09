import __main__
from typing import Dict
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

from metrics.metrics_client import MetricsClient

GATEWAY = 'localhost:9091'
JOB_NAME = __main__.__file__


class PrometheusMetrics(MetricsClient):

    def __init__(self):
        self.registry = CollectorRegistry()

    def incr(self, metric: str, tags: Dict[str, str] = {}):
        metric = metric.replace('.', '_')
        counter = Counter(metric, metric, labelnames=[list(tags.keys())], registry=self.registry)
        counter.labels(tags).inc()
        push_to_gateway(GATEWAY, job=JOB_NAME, registry=self.registry)

    def gauge(self, metric: str, value: float, tags: Dict[str, str] = {}):
        metric = metric.replace('.', '_')
        gauge = Gauge(metric, metric, labelnames=[list(tags.keys())], registry=self.registry)
        gauge.labels(tags).set(value)
        push_to_gateway(GATEWAY, job=JOB_NAME, registry=self.registry)