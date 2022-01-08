from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime, timedelta
import json
import os
from typing import Generic, TypeVar, List

GLOBAL_STORE = os.environ.get("GLOBAL_STORE") == 'True'
if GLOBAL_STORE:
    DATA_PATH = f"{os.path.expanduser('~')}/.boiler/data"
else:
    DATA_PATH = "data"

T = TypeVar('T')


class DataNotFreshException(Exception):
    pass

class DataNotFoundException(Exception):
    pass


class FileDataPersister:

    def __init__(self, id: str):
        self.id = id
    
    def save_raw_data(self, data: str) -> None:
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)
        with open(f"{DATA_PATH}/{self.id}.txt", "w") as f:
            f.write(data)
    
    def load_raw_data(self) -> str:
        try:
            with open(f"{DATA_PATH}/{self.id}.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise DataNotFoundException()

    def clear(self):
        try:
            os.remove(f"{DATA_PATH}/{self.id}.txt")
        except FileNotFoundError:
            pass
        return self
        

class StackDataPersister(Generic[T], FileDataPersister):

    def __init__(self, id: str, max_size: int):
        self.id = id
        self.max_size = max_size

    def add_stack_item(self, data: str):
        try:
            stack = json.loads(self.load_raw_data())
        except DataNotFoundException:
            stack = []
        stack.insert(0, data)
        if len(stack) > self.max_size:
            stack.pop()
        self.save_raw_data(json.dumps(stack))

    def read_stack(self) -> List[T]:
        return list(reversed(json.loads(self.load_raw_data())))


@dataclass_json
@dataclass
class FreshData(Generic[T]):
    time: datetime
    data: T

class FreshDataStore(Generic[T], StackDataPersister[T]):

    def __init__(self, id: str, max_size: int, not_fresh_threshold: timedelta):
        self.not_fresh_threshold = not_fresh_threshold
        super().__init__(id, max_size)

    def add_value(self, value: T):
        self.add_stack_item(FreshData[T](datetime.now(), value).to_json())

    def add_values(self, values: List[T]):
        for value in values:
            self.add_value(value)

    def read_all_values_since(self, freshness: timedelta) -> List[T]:
        data = [FreshData.from_json(entry) for entry in self.read_stack()]
        if data:
            last_record = data[-1:][0]
            now = datetime.now(last_record.time.tzinfo)

            if last_record.time + self.not_fresh_threshold < now:
                raise DataNotFreshException(f"Data not fresh: {self.id}")

            data = list(filter(lambda x: x.time + freshness > now, data))

            
        return [record.data for record in data]