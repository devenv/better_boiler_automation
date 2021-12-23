import json
import os
import sys
from textinput import Assistant


with open(os.path.join(sys.path[0], "device_config.json"), "r") as f:
    config = json.load(f)

with Assistant(config['device_model_id'], config['device_id']) as assistant:
    print(assistant.are_lights_on())