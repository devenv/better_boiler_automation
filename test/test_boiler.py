from unittest import TestCase
from unittest.mock import MagicMock

import os
import sys

from boiler.boiler_controller import BoilerController


class TestBoiler(TestCase):

    def setUp(self):
        self.boiler = BoilerController()
        self.boiler.assistant = MagicMock()

    def test_default_state(self):
        os.remove((os.path.join(sys.path[0], "boiler/last_state.txt")))
        self.assertEqual(self.boiler.is_on(), False)

    def test_state_after_on(self):
        self.boiler.turn_on()
        self.assertEqual(self.boiler.is_on(), True)

    def test_state_after_off(self):
        self.boiler.turn_off()
        self.assertEqual(self.boiler.is_on(), False)