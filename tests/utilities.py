"""
Utility functions related to FPDS unit tests

author: derek663@gmail.com
last_updated: 12/27/2022
"""


def read_xml_as_bytes(file_path: str, encoding="utf-8"):
    """Reads an XML file as converts it to a bytes response
    """
    with open(file_path) as data:
        bytes_data = data.read().encode(encoding)
    return bytes_data
