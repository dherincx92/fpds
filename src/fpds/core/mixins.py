import re
import xml
from xml.etree import ElementTree

from fpds.core import TREE


class fpdsMixin:
    @property
    def url_base(self) -> str:
        return "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC"

    @staticmethod
    def convert_to_lxml_tree(self) -> TREE:  # type: ignore
        """Returns lxml tree element from a bytes response"""
        tree = ElementTree.fromstring(self.content)
        return tree

    @property
    def NAMESPACE_REGEX_PATTERN(self) -> str:
        namespaces = "|".join(self.namespace_dict.values())
        # yeah, f-strings don't do well with backslashes
        PATTERN = r"\{(" + namespaces + r")\}"  # noqa
        return PATTERN
