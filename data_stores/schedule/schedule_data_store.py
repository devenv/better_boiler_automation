from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json
from typing import List

from data_stores.data_persisters import DataNotFoundException, FileDataPersister


@dataclass_json
@dataclass
class Time:
    hour: int
    minute: int
    intensity: int

    @classmethod
    def list_from_json(cls, data: str) -> List["Time"]:
        return Time.schema().load(json.loads(data), many=True)
        
    @classmethod
    def list_to_json(cls, times: List["Time"]) -> str:
        return json.dumps(Time.schema().dump(times, many=True))

    def culled(self):
        self.hour = self._cull_to_real_hour(self. hour)
        return self

    def _cull_to_real_hour(self, hour):
        if hour > 23:
            return self._cull_to_real_hour(hour - 24)
        if hour < 0:
            return self._cull_to_real_hour(hour + 24)
        return hour

    def plus_hours(self, hours: int):
        return Time(self.hour + hours, self.minute, self.intensity).culled()
        

class ScheduleDataStore(FileDataPersister):

    def __init__(self):
        super().__init__('schedule')

    def save_schedule(self, times: List[Time]) -> None:
        self.save_raw_data(Time.list_to_json(times))

    def load_schedule(self) -> List[Time]:
        try:
            data = self.load_raw_data()
        except DataNotFoundException:
            return []
        return Time.list_from_json(data)