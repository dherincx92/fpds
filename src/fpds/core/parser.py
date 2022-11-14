"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 10/16/2022
"""

import re
import requests
from typing import Dict, List

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

NAMESPACE_REGEX = r"\{(.*)\}"
DATE_REGEX = r"(\[(.*?)\])"
TRAILING_WHITESPACE_REGEX = r"\n\s+"
LAST_PAGE_REGEX = r"start=(.*?)$"
ATOM_NAMESPACE_FIELDS = ["title", "link", "modified", "content"]


class fpdsMixin:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def url_base(self) -> str:
        return "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC"

    @property
    def search_params(self):
        """Search parameters inputted by user"""
        _params = [f"{key}:{value}" for key, value in self.__dict__.items()]
        return " ".join(_params)


class _ElementAttributes(Element):
    def __init__(
        self,
        element: Element,
        namespace_dict: Dict[str, str]
    ) -> "_ElementAttributes":
        self.element = element
        self.namespace_dict = namespace_dict

    @property
    def clean_tag(self) -> str:
        """Tag name without the namespace
        """
        namespaces = "|".join(self.namespace_dict.values())
        # yeah, f-strings don't do well with backslashes
        PATTERN = "\{(" + namespaces + ")\}"
        clean_tag = re.sub(PATTERN, "", self.element.tag)
        return clean_tag

    def _generate_nested_attribute_dict(self) -> Dict[str, str]:
        """Returns all attributes of an Element

        Example
        -------
        <ns1:contractActionType description="BPA" part8OrPart13="PART8">E</ns1:contractActionType>

        The value of the `contractActionType` is "E". To help decipher
        this data, this class will parse out all attributes of the tag. This
        method will generate a nested key name structure to indicate what tag
        each attribute belongs to. In this example, the tag `contractActionType`
        has two attributes: `description` and `part8OrPart13`. This method will
        represent this tag the following way:

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


class fpdsRequest(fpdsMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_request(self):
        response = requests.get(
            url=self.url_base,
            params={"q": self.search_params}
        )
        response.raise_for_status()
        self.content = response.content
        import ipdb; ipdb.set_trace()

# TODO: have class inherit from Logger()
class fpdsXML(fpdsMixin):
    def __init__(self, content: bytes, **kwargs) -> "fpdsXML":
        self.content = content
        if self.content:
            self.tree = self.convert_to_lxml_tree()
        self.params = kwargs.keys()
        super().__init__(**kwargs)

    def parse_items(self, element: Element):
        """Returns iteration of `Element` as a generator
        """
        yield from element.iter()

    def convert_to_lxml_tree(self):
        """Returns lxml tree element from a bytes response
        """
        tree = ElementTree.fromstring(self.content)
        return tree

    @staticmethod
    def _get_full_namespace(element: Element) -> str:
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

    @property
    def response_size(self) -> int:
        """Number of entries inside each response call
        """
        return 10

    @property
    def namespace_dict(self) -> Dict[str, str]:
        """The better way of parsing tree elements with namespaces, per the docs.
        Note that `namespaces` is a list, which retains parsing order of the
        tree, which will be important in identifying Atom entries in `fpds`

        https://docs.python.org/3/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
        """
        namespaces = list()
        for element in self.parse_items(self.tree):
            _namespace = self._get_full_namespace(element)
            if _namespace not in namespaces:
                namespaces.append(_namespace)

        namespace_dict = {f'ns{idx}': ns for idx, ns in enumerate(namespaces)}
        return namespace_dict

    @property
    def total_record_count(self) -> int:
        """Total number of records in response
        """
        links = self.tree.findall('.//ns0:link', self.namespace_dict)
        last_link = list(filter(lambda link: link.get("rel") == "last", links))
        # index 0 should work since only one link should match the filter cond.
        record_count = re.search(LAST_PAGE_REGEX, last_link[0].attrib["href"])
        return int(record_count.group(1))

    def pagination_links(self):
        """FPDS contains an XML tag that provides the last link of the response.
        Within that link is the total number of records contained within the
        response. This method uses that value to build the pagination links
        """
        resp_size = self.response_size
        page_range = list(
            range(0, self.total_record_count + resp_size, resp_size)
        )
        # need to build request params first
        for page in page_range:
            link = f"{self.url_base}&q={self.search_params()}"


    def get_atom_feed_entries(self):
        """Returns
        """
        data_entries = self.tree.findall(
            './/ns0:entry',
            self.namespace_dict
        )
        return data_entries
