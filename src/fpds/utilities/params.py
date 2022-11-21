import re
from typing import Dict, List, Union

def filter_config_dict(
    config: List[Dict[str, Union[str, bool]]],
    field: str,
    value: Union[str, bool]
):
    """
    Given a configuration object, return single object from config where
    config[field] = value

    Parameters
    ----------
    config: List[Dict[str, Union[str, bool]]]
    field: str
    value: Union[str, bool]
    """
    dict = [
        field_dict for field_dict in config
        if field_dict.get(field) == value
    ]
    if len(dict) > 1:
        raise ValueError(f"Multiple objects match `{field}`=`{value}`")
    else:
        field_dict = dict[0]
    return field_dict

def raw_literal_regex_match(pattern, string ):
    raw_pattern = fr"{pattern}".replace("\\\\", "\\")
    LITERAL_PATTERN = re.compile(raw_pattern)
    match = LITERAL_PATTERN.match(string)
    return match