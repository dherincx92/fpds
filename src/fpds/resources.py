"""
Class for extracing FPDS XML resource metadata

author: derek663@gmail.com
last_updated: 06/30/2022
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List
import warnings

from fpds import fpdsElement, fpdsXML

RESOURCE_XPATH = "ns0:*"

class fpdsResources(fpdsXML):
    """
    Defines all FPDS XML elements referencing entry to the current XML feed
    or an external web resource
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _unique_resource_tags(self):
        return set(map(lambda e: e["tag"], self._resource_elements()))

    def _resource_elements(self) -> List[Dict[str, str]]:
        """
        Returns a list of XML resources and their attributes (namespace,
        tag type, text, and attributes)
        """
        resources = []
        for elem in self.root.findall(RESOURCE_XPATH, self.namespaces):
            elem = fpdsElement(elem)
            # entry tags contain metadata for each data entry
            # entries will be parsed as part of :cls:`fpdsEntries`
            if elem.tag_name != "entry":
                resources.append({
                    "namespace": elem.namespace,
                    "tag": elem.tag_name,
                    "text": elem.text,
                    "attributes": elem.attrib
                })
        return resources

    def resources(self) -> Dict[str, Dict[str, str]]:
        """
        A hierarchical organization of all XML resources. Groups XML elements
        by tag type and creates a JSON-compliant data structure.
        """
        _resources = self._resource_elements()

        # all resources are contained within the same namespace, hence the index
        namespace = _resources[0].get("namespace")
        tag_dct = [{"type": tag, "tags": []} for tag in self._unique_resource_tags]

        for dct in tag_dct:
            for rsc in _resources:
                if dct.get("type") == rsc.get("tag"):
                    rsc.pop("tag", None)
                    rsc.pop("namespace", None)
                    dct["tags"].append(rsc)

        resources = {
            "namespace": namespace,
            "resources": tag_dct
        }

        return resources
