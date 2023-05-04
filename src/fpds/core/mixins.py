from xml.etree import ElementTree


class fpdsMixin:
    @property
    def url_base(self) -> str:
        return "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC"

    @staticmethod
    def convert_to_lxml_tree(content):
        """Returns lxml tree element from a bytes response"""
        tree = ElementTree.fromstring(content)
        return tree


class fpdsXMLMixin:
    @property
    def NAMESPACE_REGEX_PATTERN(self) -> str:
        namespaces = "|".join(self.namespace_dict.values())  # type: ignore
        # yeah, f-strings don't do well with backslashes
        PATTERN = r"\{(" + namespaces + r")\}"  # noqa
        return PATTERN
