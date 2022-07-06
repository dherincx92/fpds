"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 07/06/2022
"""

import re
from typing import Dict, List
from utils.xml import extract_namespace
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

CURLY_BRACE_REGEX = "\{(.*?)\}"
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

    def top_level_elements(self) -> List[Dict[str, str]]:
        """
        Returns of top-level XML elements and their attributes (namespace,
        tag type, text, and attributes)
        """
        elements = []
        for elem in self.root.findall(RESOURCE_XPATH, self.namespaces):
            elem = fpdsElement(elem)
            # entry tags contain metadata for each data entry
            # entries will be parsed as part of :cls:`fpdsEntries`
            elements.append({
                "element": elem,
                "namespace": elem.namespace,
                "tag": elem.tag_name,
                "text": elem.text,
                "attributes": elem.attrib
            })
        return elements


class fpdsElement(Element):
    """
    A singular XML tag with cleaned properties extracted from `ElementTree`.
    """
    def __init__(self, elem):
        self.elem = elem

    def __repr__(self):
        return f"<fpdsElement {self.elem.tag}>"

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
        Extracts namesapce from XML element tag attribute
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
