import os

from datadog import initialize, statsd

STATS_ENABLED = os.getenv('STATS_ENABLED') == 'True'


class Metrics:

    options = {
        'statsd_host':'127.0.0.1',
        'statsd_port':8125
    }

    if STATS_ENABLED:
        initialize(**options)

    def incr(self, metric, tags={}):
        if STATS_ENABLED:
            statsd.increment(metric, tags)

    def gauge(self, metric, value, tags={}):
        if STATS_ENABLED:
            statsd.gauge(metric, value, tags)

    def event(self, title, message, alert_type='success'):
        if STATS_ENABLED:
            statsd.event(title, message, alert_type=alert_type)