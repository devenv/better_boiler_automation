import json
from dataclasses import dataclass
import os
import sys

def load_config():
    with open(os.path.join(sys.path[0], "scheduler/scheduler_config.json"), "r") as f:
        return json.load(f)

@dataclass
class Time:
    hour: int
    minute: int
    intencity: int


class SchedulerConfig:

    TIME_ZONE = 2
    config = load_config()

    def __init__(self):
        self.times = [Time(item['hour'] - self.TIME_ZONE, item['minute'], item['intencity']) for item in self.config]