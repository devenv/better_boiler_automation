import asyncio

from aioswitcher.api import SwitcherV2Api
from aioswitcher import consts

from utils.secrets import load_dict


class Switcher:

    def __init__(self):
        self.config = load_dict("switcher_config")

    def is_on(self):
        return self._with_loop(self._is_on())
    
    async def _is_on(self) -> bool:
        async with SwitcherV2Api(asyncio.get_event_loop(), self.config['ip'], None, self.config['device_id'], None) as swapi:
            state_response = await swapi.get_state()
            return state_response.state == "on"

    def turn_on(self) -> None:
        self._with_loop(self._turn_on())

    async def _turn_on(self) -> bool:
        async with SwitcherV2Api(asyncio.get_event_loop(), self.config['ip'], None, self.config['device_id'], None) as swapi:
            await swapi.control_device(consts.COMMAND_ON)

    def turn_off(self) -> None:
        self._with_loop(self._turn_off())

    async def _turn_off(self) -> bool:
        async with SwitcherV2Api(asyncio.get_event_loop(), self.config['ip'], None, self.config['device_id'], None) as swapi:
            await swapi.control_device(consts.COMMAND_OFF)

    def _with_loop(self, func):
        loop = asyncio.new_event_loop()
        result = asyncio.get_event_loop().run_until_complete(func)
        loop.close()
        return result