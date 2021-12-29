from datadog import initialize, statsd


class Metrics:

    options = {
        'statsd_host':'127.0.0.1',
        'statsd_port':8125
    }

    initialize(**options)

    def incr(self, metric, tags):
        statsd.increment(metric, tags)
