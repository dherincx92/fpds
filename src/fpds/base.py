"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 07/06/2022
"""
from datetime import datetime
from pathlib import Path
import os
import re
from tkinter import LAST
from typing import Dict, List

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element


CURLY_BRACE_REGEX = r"\{(.*?)\}"
DATE_REGEX = r"(\[(.*?)\])"
TRAILING_WHITESPACE_REGEX = r"\n\s+"
LAST_PAGE_REGEX = r"(?<=start=).*"
RESOURCE_XPATH = "ns0:*"

DUMP_DIR = Path.home() / ".fpds"


class fpdsXML:
    """
    Generic methods for FPDS XML that will be inherited by both the
    container and metadata Atom feed elements, as prescribed at
    `https://www.fpds.gov/wiki/index.php/Atom_Feed_Specifications_V_1.5.2`

    Args:
      - file (str): Path to a valid XML file
    """
    def __init__(self, file: str = None, xml_string: str = None) -> "fpdsXML":
        self.file = file
        self.xml_string = xml_string
        self.encoding = 'utf-8'

        if self.file and self.xml_string:
            message = "Cannot provide values for both `file` and `xml_string`"
            raise ValueError(message)

        if self.file:
            self.tree = ET.parse(self.file)
        else:
            self.tree = ET.ElementTree(ET.fromstring(xml_string))
            # we need this value in order to access the namespace property
            self.file = os.path.join(
                DUMP_DIR,
                f"fpds_contracts_{datetime.now().strftime('%Y_%m_%d')}"
            )
            self.dump_xml()

        self.root = self.tree.getroot()

    def dump_xml(self):
        if not os.path.exists(DUMP_DIR):
            os.mkdir(DUMP_DIR)
        self.tree.write(self.file, self.encoding)

    def xml_date_range(self):
        title = self.tree.find("ns0:title", self.namespaces).text

        # should yield something like this: '[2022/05/02,2033/05/30]'
        _date = re.search(DATE_REGEX, title).group()
        # removes square brackets
        _date = _date[1:-1]
        date = _date.replace(",", "__").replace("/", "_")

        return date

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
    def data_entries(self):
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
    def response_record_count(self):
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

    def record_links(self):
        """List of paginated links for entire XML response"""
        params = (
            lambda x: x.get("attributes").get("rel") == "last",
            self.top_level_elements()
        )
        last_link = list(filter(*params))
        href = last_link[0].get("attributes").get("href")

        total_records = re.search(LAST_PAGE_REGEX, href).group()
        endpoint = href.split("&start")[0]

        _links = []
        for page in range(0, int(total_records) + 10, 10):
            link = f"{endpoint}&start={page}"
            _links.append(link)

        return _links






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

    @property
    def raw_tag(self):
        """The tag attribute from `ET.Element`, which includes the namespace"""
        return self.elem.tag

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
