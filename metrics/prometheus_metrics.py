import __main__
from typing import Dict
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway

from metrics.metrics_client import MetricsClient

GATEWAY = 'localhost:9091'
JOB_NAME = __main__.__file__


class PrometheusMetrics(MetricsClient):

    known_metrics = {}
    registry = CollectorRegistry()

    def incr(self, metric: str, tags: Dict[str, str] = {}):
        metric = metric.replace('.', '_')
        if metric in self.known_metrics:
            counter = self.known_metrics[metric]
        else:
            counter = Counter(metric, metric, labelnames=list(tags.keys()), registry=self.registry)
            self.known_metrics[metric] = counter
        if tags:
            counter = counter.labels(tags)
        counter.inc()
        push_to_gateway(GATEWAY, job=JOB_NAME, registry=self.registry)

    def gauge(self, metric: str, value: float, tags: Dict[str, str] = {}):
        metric = metric.replace('.', '_')
        if metric in self.known_metrics:
            gauge = self.known_metrics[metric]
        else:
            gauge = Gauge(metric, metric, labelnames=list(tags.keys()), registry=self.registry)
            self.known_metrics[metric] = gauge
        if tags:
            gauge = gauge.labels(tags)
        gauge.set(value)
        push_to_gateway(GATEWAY, job=JOB_NAME, registry=self.registry)