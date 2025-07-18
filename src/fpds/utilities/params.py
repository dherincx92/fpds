"""
Utility functions related to FPDS request parameters

author: derek663@gmail.com
last_updated: 01/20/2024
"""

import re
from typing import Any, Dict, List, Optional, TypedDict, Union, cast

from fpds.config import FPDS_FIELDS_CONFIG as FIELDS
from fpds.errors import (
    fpdsDuplicateParameterConfiguration,
    fpdsInvalidParameter,
    fpdsMismatchedParameterRegexError,
)

CONFIG_TYPE = List[Dict[str, Any]]


class ParameterConfig(TypedDict):
    description: str
    name: str
    quotes: bool
    regex: str


def get_search_param_from_config(
    name: str, config: CONFIG_TYPE = FIELDS
) -> ParameterConfig:
    """Finds the name of a kwarg in `fields.json`."""
    field_config = [field for field in config if field.get("name") == name]
    if not field_config:
        raise fpdsInvalidParameter(name=name)
    elif len(field_config) > 1:
        raise fpdsDuplicateParameterConfiguration(name=name)
    return cast(ParameterConfig, field_config[0])


def match_regex_with_literal_string_pattern(
    pattern: str,
    string: str,
) -> Optional[re.Match[str]]:
    """Converts a regex pattern into a raw literal string to be used by
    Python's regex module.

    This function was written out of a need of escaping single backslahes
    with double backslahes in JSON. See `constants/fields.json` for examples.
    """
    _string = str(string) if not isinstance(string, str) else string
    raw_pattern = rf"{pattern}".replace("\\\\", "\\")
    LITERAL_PATTERN = re.compile(raw_pattern)
    match = LITERAL_PATTERN.match(_string)
    return match


def validate_kwarg(kwarg: str, string: str) -> str:
    """Validates a kwarg name and ensures value matches specified regex."""
    obj = get_search_param_from_config(name=kwarg)
    pattern = obj["regex"]
    match = match_regex_with_literal_string_pattern(pattern=pattern, string=string)
    if not match:
        raise fpdsMismatchedParameterRegexError(string=string, pattern=pattern)

    if obj.get("quotes"):
        return f'"{string}"'
    else:
        return string
