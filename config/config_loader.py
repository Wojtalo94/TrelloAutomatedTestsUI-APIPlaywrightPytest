import yaml
import os
from dotenv import load_dotenv


def load_test_config(path="config/browser_config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)


# wczytujemy zmienne z pliku .env
load_dotenv()
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")