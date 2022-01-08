import json
import os

GLOBAL_STORE = os.environ.get("GLOBAL_STORE") == 'True'
if GLOBAL_STORE:
    SECRETS_PATH = f"{os.path.expanduser('~')}/.boiler/secrets"
else:
    SECRETS_PATH = "secrets"


def load_dict(file: str) -> dict:
    with open(f"{SECRETS_PATH}/{file}.json", "r") as f:
        return json.load(f)
    
def load_string(file):
    with open(f"{SECRETS_PATH}/{file}.txt", "r") as f:
        return f.readline().strip()