from datetime import timedelta

from data_stores.data_persisters import FreshDataStore


FRESHNESS = timedelta(minutes=10)
MAX_SIZE = 100


class CloudsDataStore(FreshDataStore[float]):
    
    def __init__(self):
        super().__init__('clouds', MAX_SIZE, FRESHNESS)


class TemperatureDataStore(FreshDataStore[float]):
    
    def __init__(self):
        super().__init__('temperature', MAX_SIZE, FRESHNESS)
