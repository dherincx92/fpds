"""
Utility functions related to FPDS request parameters

author: derek663@gmail.com
last_updated: 12/24/2022
"""
import re
from typing import Dict, List, Union


def filter_config_dict(
    config: List[Dict[str, Union[str, bool]]],
    field: str,
    value: Union[str, bool]
):
    """Given a configuration object, return single object from config where
    config[field] = value

    Parameters
    ----------
    config: List[Dict[str, Union[str, bool]]]
    field: str
    value: Union[str, bool]
    """
    dct = [
        field_dict for field_dict in config
        if field_dict.get(field) == value
    ]
    if len(dct) > 1:
        raise ValueError(f"Multiple objects match `{field}`=`{value}`")
    else:
        field_dict = dct[0]
    return field_dict


def raw_literal_regex_match(pattern, string):
    """Converts a regex pattern into a raw literal string to be used by
    Python's regex module.

    This function was written out of a need of escaping single backslahes
    with double backslahes in JSON. See `constants/fields.json` for examples
    """
    raw_pattern = fr"{pattern}".replace("\\\\", "\\")
    LITERAL_PATTERN = re.compile(raw_pattern)
    match = LITERAL_PATTERN.match(string)
    return match
