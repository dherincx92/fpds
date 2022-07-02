import re
from pathlib import Path

TMP_XML_FOLDER = "fpds"
TMP_FILE_NAME = "tmp.xml"
TMP_XML_FILE = Path.home() / TMP_XML_FOLDER / TMP_FILE_NAME
CURLY_BRACE_REGEX = "\{(.*?)\}"

def dump_xml_file(tree):
    """
    Provides a temporary XML file generated from FPDS' Atom feed. This is
    a necessary step since :class:`ElementTree` `.iterparse` method requires
    a filename or file object.
    """
    with open(TMP_XML_FILE, 'w') as stream:
         tree.write(stream, encoding='unicode')

def extract_namespace(tag):
    """
    Extracts namesapce from XML element
    """
    pattern = re.compile(CURLY_BRACE_REGEX)
    result = pattern.search(tag)
    if result:
        return result.group(1)
