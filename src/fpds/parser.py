"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 07/06/2022
"""

import os
import re
from typing import Dict

from xml.etree import ElementTree
from xml.etree.ElementTree import Element


NAMESPACE_REGEX = r"\{(.*)\}"
DATE_REGEX = r"(\[(.*?)\])"
TRAILING_WHITESPACE_REGEX = r"\n\s+"
LAST_PAGE_REGEX = r"(?<=start=).*"
ATOM_NAMESPACE_FIELDS = ["title", "link", "modified", "content"]

class _ElementAttributes(Element):
    def __init__(
        self,
        element: Element,
        namespace_dict: Dict[str, str]
    ) -> "_ElementAttributes":
        self.element = element
        self.namespace_dict = namespace_dict

    @property
    def clean_tag(self):
        namespaces = "|".join(self.namespace_dict.values())
        # yeah, f-strings don't do well with backslashes
        PATTERN = "\{(" + namespaces + ")\}"
        clean_tag = re.sub(PATTERN, "", self.element.tag)
        return clean_tag

    def _generate_nested_attribute_dict(self) -> Dict[str, str]:
        """Returns all tag attributes of an Element

        Example
        -------
        <ns1:contractActionType description="BPA" part8OrPart13="PART8">E</ns1:contractActionType>

        The value of the `contractActionType` is "E"; this requires users to
        download an FPDS Data Dictionary and decipher what "E" means.
        To help decipher this data, this class will parse out all
        attributes of the tag. This method will generate a nested key name
        structure to indicate what tag each attribute belongs to. In this
        example, the tag `contractActionType` has two attributes: `description`
        and `part8OrPart13`. This method will represent this tag the following
        way:

            {
                "contractActionType": "E",
                "contractActionType__description": "BPA"
                "contractActionType__part8OrPart13": "PART8"
            }
        """
        attributes = self.element.attrib
        _attributes_copy = attributes.copy()

        tag = self.clean_tag
        for key in attributes:
            nested_key = f"{tag}__{key}"
            _attributes_copy[nested_key] = attributes[key]
            del _attributes_copy[key]
        return _attributes_copy


# TODO: have class inherit from Logger()
class fpdsMixin:
    def __init__(self, content: bytes) -> "fpdsMixin":
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

    @property
    def namespace_dict(self):
        """The better way of parsing tree elements with namespaces, per the docs.
        Note that `namespaces` is a list, which retains parsing order of the
        tree, which will be important in identifying Atom entries in `fpds`

        https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
        """
        namespaces = list()
        for element in self.parse_tree_elements():
            _namespace = self._get_full_namespace(element)
            if _namespace not in namespaces:
                namespaces.append(_namespace)

        namespace_dict = {f'ns{idx}': ns for idx, ns in enumerate(namespaces)}
        return namespace_dict

class fpds(fpdsMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def parse_entry(self):
        data_entries = self.tree.findall(
            './/ns0:entry',
            self.namespace_dict
        )
