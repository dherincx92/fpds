from xml.etree.ElementTree import Element, ElementTree, fromstring


class fpdsMixin:
    @property
    def url_base(self) -> str:
        return "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC"

    @staticmethod
    def convert_to_lxml_tree(content) -> ElementTree:
        """Returns lxml tree element from a bytes response"""
        tree = ElementTree(fromstring(content))
        return tree


class fpdsXMLMixin:
    @property
    def xml_child_classes(self):
        """Classes from the `xml` API that inherit from `ElementTree` module"""
        return (ElementTree, Element)

    @property
    def xml_child_classes_with_modules(self):
        """Fully qualified module name for classes in `xml_child_classes`"""
        classes = (ElementTree, Element)
        with_modules = [cls.__module__ + f".{cls.__qualname__}" for cls in classes]
        return with_modules

    @property
    def NAMESPACE_REGEX_PATTERN(self) -> str:
        namespaces = "|".join(self.namespace_dict.values())  # type: ignore
        # yeah, f-strings don't do well with backslashes
        PATTERN = r"\{(" + namespaces + r")\}"  # noqa
        return PATTERN
