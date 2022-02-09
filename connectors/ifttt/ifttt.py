import requests
from typing import Dict

from utils.logger import get_logger
from utils.secrets import load_string


class Ifttt:

    EVENT_NAME = 'boiler'

    def __init__(self):
        self.key = load_string("ifttt_key")
    
    def send_json(self, data: Dict[str, str]):
        requests.post(f'https://maker.ifttt.com/trigger/{self.EVENT_NAME}/json/with/key/{self.key}', json=data, headers={'Content-Type': 'application/json'})