from abc import ABC, abstractmethod


class MetricsClient(ABC):

    @abstractmethod
    def incr(self, metric, amount=1, tags={}):
        pass

    @abstractmethod
    def gauge(self, metric, value, tags={}):
        pass