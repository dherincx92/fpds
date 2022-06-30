import re
import xml.etree.ElementTree as ET
from typing import Dict

CURLY_BRACE_REGEX = "\{(.*?)\}"
RESOURCE_XPATH = "ns0:*"

class fpdsXML:
    """
    Generic methods for FPDS XML that will be inherited by both the
    container and metadata Atom feed elements, as prescribed at
    `https://www.fpds.gov/wiki/index.php/Atom_Feed_Specifications_V_1.5.2`
    """
    def __init__(self, file):
        self.file = file
        self.namespaces = self._get_xml_namespaces()

    def _get_xml_namespaces(self) -> Dict[str, str]:
        """
        Returns all namepaces existing in an XML file

        Note: Although there is no way to identify a default namespace, all
        python dictionaries are ordered dictionaries so we assume that the
        order of this method reflects actual XML hierarchy
        """
        namespaces = dict([
            node for _, node in ET.iterparse(self.file, events=["start-ns"])
        ])
        return namespaces


class fpdsElement:
    def __init__(self, elem):
        self.elem = elem

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
        Extracts namesapce from XML element
        """
        pattern = re.compile(CURLY_BRACE_REGEX)
        result = pattern.search(self.elem.tag)
        if result:
            return result.group(0)

    @property
    def text(self):
        return self.elem.text

    @property
    def attrib(self):
        return self.elem.attrib


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
