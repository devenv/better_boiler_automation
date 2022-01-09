from abc import ABC, abstractmethod


class MetricsClient(ABC):

    @abstractmethod
    def incr(self, metric, tags={}):
        pass

    @abstractmethod
    def gauge(self, metric, value, tags={}):
        pass