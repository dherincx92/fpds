from datetime import datetime
from pathlib import Path

from .config import FPDS_DATA_DIR
from .core.parser import fpdsRequest, fpdsXML

CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
FPDS_DATA_DATE_DIR = FPDS_DATA_DIR / CURRENT_DATE
FPDS_DATA_DATE_DIR.mkdir(parents=True, exist_ok=True)

__all__ = [
    "fpdsRequest",
    "fpdsXML"
]
