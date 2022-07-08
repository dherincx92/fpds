"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 07/06/2022
"""

import re
from typing import Dict, List
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

CURLY_BRACE_REGEX = r"\{(.*?)\}"
TRAILING_WHITESPACE_REGEX = r"\n\s+"
RESOURCE_XPATH = "ns0:*"


class fpdsXML:
    """
    Generic methods for FPDS XML that will be inherited by both the
    container and metadata Atom feed elements, as prescribed at
    `https://www.fpds.gov/wiki/index.php/Atom_Feed_Specifications_V_1.5.2`

    Args:
      - file (str): Path to a valid XML file
    """
    def __init__(self, file: str) -> "fpdsXML":
        self.file = file
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()

    @property
    def namespaces(self) -> Dict[str, str]:
        """
        Returns all namepaces existing in an XML file

        Note: Although there is no way to identify a default namespace, all
        python dictionaries are ordered dictionaries so we assume that the
        order of the resulting dict reflects actual XML hierarchy
        """
        namespaces = dict([
            node for _, node in ET.iterparse(self.file, events=["start-ns"])
        ])
        return namespaces

    @property
    def data_records(self):
        """
        Returns all data record elements

        Tags containing record data are labeled as follows: `<entry></entry>`
        """
        _data_records = []
        for elem in self.top_level_elements():
            if elem.get("tag") == "entry":
                fpds_elem = fpdsElement(elem.get("element"))
                _data_records.append(fpds_elem)
        return _data_records

    @property
    def record_count(self):
        """Returns the number of data records contained within the XML"""
        _record_count = len(self.data_records)
        return _record_count

    def top_level_elements(self) -> List[Dict[str, str]]:
        """
        Returns of top-level XML elements and their attributes (namespace,
        tag type, text, and attributes)
        """
        elements = []
        for elem in self.root.findall(RESOURCE_XPATH, self.namespaces):
            elem = fpdsElement(elem)()
            # entry tags contain metadata for each data entry
            # entries will be parsed as part of :cls:`fpdsEntries`
            elements.append(elem)
        return elements


class fpdsElement(Element):
    """
    A singular XML tag with cleaned properties extracted from `ElementTree`

    Args:
        - elem (ET.Element): xml Element
    """
    def __init__(self, elem: Element):
        self.elem = elem

    def __repr__(self):
        return f"<fpdsElement {self.elem.tag}>"

    def __call__(self):
        """Element metadata should be returned if this class is called"""
        elem_dct = {
            "element": self.elem,
            "namespace": self.namespace,
            "tag": self.tag_name,
            "text": self.text,
            "attributes": self.attrib
        }
        return elem_dct

    @staticmethod
    def clean_trailing_whitespace(string):
        """
        Removes trailing whitespace from a string
        """
        return re.sub(TRAILING_WHITESPACE_REGEX, "", string)

    @property
    def tag_name(self):
        """
        Cleans up the namesapce from an Element class object
        """
        clean_tag = re.sub(CURLY_BRACE_REGEX, "", self.elem.tag)
        return clean_tag

    @property
    def namespace(self):
        """
        Extracts namespace from XML element tag attribute
        """
        pattern = re.compile(CURLY_BRACE_REGEX)
        result = pattern.search(self.elem.tag)
        if result:
            return result.group(1)

    @property
    def text(self):
        """XML tag text attribute"""
        return self.elem.text

    @property
    def attrib(self):
        """XML tag attributes mapping"""
        return self.elem.attrib
