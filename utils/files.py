import json
import os
import sys


def load_dict(file: str) -> dict:
    with open(os.path.join(sys.path[0], file), "r") as f:
        return json.load(f)
    
def load_string(file):
    with open(os.path.join(sys.path[0], file)) as f:
        return f.readline().strip()