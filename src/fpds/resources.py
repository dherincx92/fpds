"""
Class for extracing FPDS XML resource metadata

author: derek663@gmail.com
last_updated: 06/30/2022
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict

from fpds import fpdsElement, fpdsXML

RESOURCE_XPATH = "ns0:*"

class fpdsResources(fpdsXML):
    """
    Defines all FPDS XML elements referencing entry to the current XML feed
    or an external web resource
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()

    def parse_resource_metadata(self):
        namespaces = self._get_xml_namespaces()

        metadata = []
        for elem in self.root.findall(RESOURCE_XPATH, namespaces):
            elem = fpdsElement(elem)
            # entry tags contain metadata for each data entry
            if elem.tag_name != "entry":
                metadata.append(elem)
        return metadata

    def transformed_xml_resources(self):
        """
        Returns a list of XML resources from an FPDS Atom feed result
        """
        element_metadata = [
            {
                "namespace": elem.namespace,
                "tag": elem.tag_name,
                "text": elem.text,
                "attributes": elem.attrib
            }
            for elem in self.parse_resource_metadata()
        ]
        return element_metadata
