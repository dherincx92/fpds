"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 07/06/2022
"""

import os
import re
from unicodedata import name

from xml.etree import ElementTree
from xml.etree.ElementTree import Element


NAMESPACE_REGEX = r"\{(.*)\}"
DATE_REGEX = r"(\[(.*?)\])"
TRAILING_WHITESPACE_REGEX = r"\n\s+"
LAST_PAGE_REGEX = r"(?<=start=).*"

class fpds:
    def __init__(self, content: bytes) -> "fpds":
        self.content = content
        self.tree = self.convert_to_lxml_tree()

    def convert_to_lxml_tree(self) -> Element:
        """Returns lxml tree element
        """
        tree = ElementTree.fromstring(self.content)
        return tree

    @staticmethod
    def _get_full_namespace(element: Element):
        """For some odd reason, the lxml API doesn't have a method to provide
        namespaces natively unless an XML file is saved locally. To avoid this,
        we just do some regex work

        Parameters
        ----------
        element: Element
            An lxml Element type
        """
        namespace = re.match(NAMESPACE_REGEX, element.tag)
        return namespace.group(1) if namespace else ''

    def parse_tree_elements(self):
        """Returns iteration of tree as a generator
        """
        yield from self.tree.iter()

    def _generate_namespace_dict(self):
        """The better way of parsing tree elements with namespaces, per the docs
        https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
        """
        namespaces = set()
        for element in self.parse_tree_elements():
            _namespace = self._get_full_namespace(element)
            if _namespace not in namespaces:
                namespaces.add(_namespace)

        namespace_dict = {f'ns{idx}': ns for idx, ns in enumerate(namespaces)}
        return namespace_dict


