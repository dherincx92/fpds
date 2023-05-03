from xml.etree import ElementTree

from fpds.core import TREE


class fpdsMixin:
    @property
    def url_base(self) -> str:
        return "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC"

    def convert_to_lxml_tree(self) -> None:  # type: ignore
        """Returns lxml tree element from a bytes response"""
        if isinstance(self.content, list):
            self.content = [ElementTree.fromstring(_content) for _content in self.content]
        else:
            self.content = ElementTree.fromstring(self.content)


class fpdsXMLMixin:
    @property
    def NAMESPACE_REGEX_PATTERN(self) -> str:
        namespaces = "|".join(self.namespace_dict.values())
        # yeah, f-strings don't do well with backslashes
        PATTERN = r"\{(" + namespaces + r")\}"  # noqa
        return PATTERN
