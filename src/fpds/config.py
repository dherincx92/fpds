"""
Configurations and constants

author: derek663@gmail.com
last_updated: 11/15/2022
"""
import json
from importlib.resources import files
from pathlib import Path

FIELDS_FILE = "fields.json"
FPDS_FIELDS_FILE = files("src.fpds.core.constants").joinpath(FIELDS_FILE)

with Path(FPDS_FIELDS_FILE).open(encoding="utf-8") as file:
    FIELDS_FILE_CONFIG = json.load(file)