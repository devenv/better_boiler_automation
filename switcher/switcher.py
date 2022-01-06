import asyncio
import json
import os
import sys

from aioswitcher.api import SwitcherApi, Command
from aioswitcher.device import DeviceState

def load_config():
    with open(os.path.join(sys.path[0], "switcher/switcher_config.json"), "r") as f:
        return json.load(f)


class Switcher:

    def __init__(self):
        self.config = load_config()

    def is_on(self):
        return self._with_loop(self._is_on())
    
    async def _is_on(self) -> bool:
        async with SwitcherApi(self.config['ip'], self.config['device_id']) as swapi:
            state_response = await swapi.get_state()
            return state_response.state == DeviceState.ON

    def turn_on(self) -> None:
        self._with_loop(self._turn_on())

    async def _turn_on(self) -> bool:
        async with SwitcherApi(self.config['ip'], self.config['device_id']) as swapi:
            await swapi.control_device(Command.ON)

    def turn_off(self) -> None:
        self._with_loop(self._turn_off())

    async def _turn_off(self) -> bool:
        async with SwitcherApi(self.config['ip'], self.config['device_id']) as swapi:
            await swapi.control_device(Command.OFF)

    def _with_loop(self, func):
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(func)
        loop.close()
        return result