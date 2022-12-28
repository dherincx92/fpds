"""
Configurations and constants

author: derek663@gmail.com
last_updated: 12/27/2022
"""
import json
from datetime import datetime
from importlib.resources import files
from pathlib import Path

HOME = Path.home()
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")

# FPDS-specific configurations
FPDS_DATA_DIR = HOME / ".fpds"
FPDS_FIELDS_FILE = "fields.json"
FPDS_FIELDS_FILE_PATH = files("fpds.constants").joinpath(FPDS_FIELDS_FILE)
FPDS_DATA_DATE_DIR = FPDS_DATA_DIR / CURRENT_DATE

# actions
FPDS_DATA_DATE_DIR.mkdir(parents=True, exist_ok=True)

with Path(FPDS_FIELDS_FILE_PATH).open(encoding="utf-8") as file:
    FPDS_FIELDS_CONFIG = json.load(file)
