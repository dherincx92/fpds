"""
Configurations and constants

author: derek663@gmail.com
last_updated: 11/15/2022
"""
import json
from importlib.resources import files
from pathlib import Path

HOME = Path.home()

# FPDS-specific configurations
FPDS_DATA_DIR = HOME / ".fpds"
FPDS_FIELDS_FILE = "fields.json"
FPDS_FIELDS_FILE_PATH = files("fpds.constants").joinpath(FPDS_FIELDS_FILE)

with Path(FPDS_FIELDS_FILE_PATH).open(encoding="utf-8") as file:
    FPDS_FIELDS_CONFIG= json.load(file)