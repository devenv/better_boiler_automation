import json
from dataclasses import dataclass
import os
import sys

def load_config():
    with open(os.path.join(sys.path[0], "scheduler/calendar_config.json"), "r") as f:
        return json.load(f)

@dataclass
class Time:
    hour: int
    minute: int
    intensity: int


class SchedulerConfig:

    TIME_ZONE = 2
    config = load_config()

    def __init__(self):
        self.times = [Time(self.cull_to_real_hour(item['hour'] - self.TIME_ZONE), item['minute'], item['intensity']) for item in self.config]

    def cull_to_real_hour(self, hour):
        if hour > 23:
            return self.cull_to_real_hour(hour - 24)
        if hour < 0:
            return self.cull_to_real_hour(hour + 24)
        return hour