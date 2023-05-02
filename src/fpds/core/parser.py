"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 05/02/2023
"""

import re
from itertools import chain
from typing import Dict, Iterator, List, Optional, Union
from xml.etree.ElementTree import Element

import requests
from tqdm import tqdm

from fpds.config import FPDS_FIELDS_CONFIG as FIELDS
from fpds.core import TREE
from fpds.core.mixins import fpdsMixin
from fpds.utilities import filter_config_dict, raw_literal_regex_match

NAMESPACE_REGEX = r"\{(.*)\}"
WHITESPACE_REGEX = r"\n\s+"
LAST_PAGE_REGEX = r"start=(.*?)$"


class fpdsRequest(fpdsMixin):
    """Makes a GET request to the FPDS ATOM feed. Takes an unlimited number of
    arguments. All query parameters should be submitted as strings. During
    class instantiation, this class will validate argument names and values and
    raise a `ValueError` if any error exists.

    Example:
        request = fpdsRequest(
            LAST_MOD_DATE="[2022/01/01, 2022/05/01]",
            AGENCY_CODE="7504"
        )

    Parameters
    ----------
    cli_run: `bool`
        Flag indicating if this class is being isntantiated by a CLI run
        Defaults to `False`

    Raises
    ------
    ValueError:
        Raised if no keyword argument(s) are provided, a keyword argument
        is not a valid FPDS parameter, or the value of a keyword argument
        does not match the expected regex.
    """

    def __init__(self, cli_run: bool = False, **kwargs):
        self.cli_run = cli_run
        self.content = []  # type: List[TREE]
        if kwargs:
            self.kwargs = kwargs
        else:
            raise ValueError("You must provide at least one keyword parameter")

        # do not run class validations since CLI command has its own
        if not self.cli_run:
            self.valid_fields = [field.get("name") for field in FIELDS]
            for kwarg, value in self.kwargs.items():
                if kwarg not in self.valid_fields:
                    raise ValueError(f"`{kwarg}` is not a valid FPDS parameter")
                else:
                    kwarg_dict = filter_config_dict(FIELDS, "name", kwarg)
                    kwarg_regex = kwarg_dict.get("regex")
                    match = raw_literal_regex_match(kwarg_regex, value)
                    if not match:
                        raise ValueError(
                            f"`{value}` does not match regex: {kwarg_regex}"
                        )
                    if kwarg_dict.get("quotes"):
                        self.kwargs[kwarg] = f'"{value}"'

    def __str__(self) -> str:
        """String representation of `fpdsRequest`"""
        kwargs_str = " ".join([f"{key}={value}" for key, value in self.kwargs.items()])
        return f"<fpdsRequest {kwargs_str}>"

    def __call__(self):
        """Shortcut for making an API call and retrieving content"""
        records = self.parse_content()
        return records

    @property
    def search_params(self):
        """Search parameters inputted by user"""
        _params = [f"{key}:{value}" for key, value in self.kwargs.items()]
        return " ".join(_params)

    def send_request(self, url: Optional[str] = None):
        """Sends request to FPDS Atom feed

        Parameters
        ----------
        url: `str`, optional
            A URL to send a GET request to. If not provided, this method
            will default to using `url_base`
        """
        response = requests.get(
            url=self.url_base if not url else url, params={"q": self.search_params}
        )
        response.raise_for_status()
        content_tree = self.convert_to_lxml_tree(response)
        self.content.append(content_tree)

    def create_content_iterable(self):
        """Paginates through response and creates an iterable of XML trees.
        This method will not have a return but rather, will set the `content`
        attribute to an iterable of XML ElementTrees'
        """
        self.send_request()
        params = self.search_params
        tree = fpdsXML(self.content[0])

        links = tree.pagination_links(params=params)
        if len(links) > 1:
            links.pop(0)
            for link in links:
                self.send_request(link)

    def parse_content(self) -> List[Dict[str, Union[str, int, float]]]:
        """Parses a content iterable and generates a list of records"""
        self.create_content_iterable()
        records = []
        for tree in tqdm(self.content):
            xml = fpdsXML(content=tree)
            records.append(xml.jsonified_entries())
        return list(chain.from_iterable(records))


class fpdsXML(fpdsMixin):
    """Parses FPDS request content received as bytes or `xml.etree.ElementTree`

    Parameters
    ----------
    content: `Union[bytes, TREE]`
        Bytes content or an ElementTree element that can be parsed into
        valid XML.

    Raises
    ------
    TypeError:
        If `content` is not of type `bytes` or an instance of
        `xml.etree.ElementTree.Element`.
    """

    def __init__(self, content: Union[bytes, TREE]) -> None:
        if isinstance(content, bytes):
            self.content = content
            self.tree = self.convert_to_lxml_tree()
        if isinstance(content, TREE):
            self.tree = content
        if not isinstance(content, (bytes, TREE)):
            raise TypeError(
                "You must provide bytes content or an instance of "
                "`xml.etree.ElementTree.Element`"
            )

    def __str__(self):
        return f"<fpdsXML {self.content.tag}>"

    def parse_items(self, element: Element) -> Iterator[TREE]:
        """Returns iteration of `Element` as a generator"""
        yield from element.iter()

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
        return namespace.group(1) if namespace else ""

    @property
    def response_size(self) -> int:
        """Max number of records in a single response"""
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

        namespace_dict = {f"ns{idx}": ns for idx, ns in enumerate(namespaces)}
        return namespace_dict

    @property
    def total_record_count(self) -> int:
        """Total number of records across all pagination links."""
        links = self.tree.findall(".//ns0:link", self.namespace_dict)
        last_link = [link for link in links if link.get("rel") == "last"]
        if last_link:
            # length of last_link should always be 1
            match = re.search(LAST_PAGE_REGEX, last_link[0].attrib["href"])
            assert match is not None
            record_count = int(match.group(1))
        else:
            record_count = len(self.get_atom_feed_entries())
        return record_count

    def pagination_links(self, params: str) -> List[str]:
        """Builds pagination links for a single API response based on the
        total record count value
        """
        resp_size = self.response_size
        offset = 0 if self.total_record_count <= 10 else resp_size
        page_range = list(range(0, self.total_record_count + offset, resp_size))
        page_links = []
        for num in page_range:
            link = f"{self.url_base}&q={params}&start={num}"
            page_links.append(link)
        return page_links

    def get_atom_feed_entries(self) -> List[TREE]:
        """Returns tree entries that contain FPDS record data"""
        data_entries = self.tree.findall(".//ns0:entry", self.namespace_dict)
        return data_entries

    # @jsonify
    def jsonified_entries(self):
        """Returns all paginated entries from an FPDS request as valid JSON"""
        entries = self.get_atom_feed_entries()
        json_data = [Entry(content=entry)() for entry in entries]
        return json_data


class fpdsElement(fpdsXML):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def NAMESPACE_REGEX_PATTERN(self) -> str:
        """A single regex pattern string that allows us to remove all
        namespaces from tags, irrespective of namespace value.
        """
        namespaces = "|".join(self.namespace_dict.values())
        # yeah, f-strings don't do well with backslashes
        PATTERN = r"\{(" + namespaces + r")\}"  # noqa

        return PATTERN

    @property
    def clean_tag(self) -> str:
        """Tag name without the namespace. A tag like the following:
        `ns1:productOrServiceInformation` would simply return
        `productOrServiceInformation`
        """
        clean_tag = re.sub(self.NAMESPACE_REGEX_PATTERN, "", self.tree.tag)
        return clean_tag


class EmptyParentName(str):
    """Class representation of tag with no parent name"""

    def __new__(cls):
        return ""


class _ElementAttributes(fpdsElement, fpdsMixin):
    """
    Utility class that helps parse out extra features of XML tags generated
    by `xml.etree.ElementTree.Element`. This class should ideally not be
    instantiated by users.

    Parameters
    ----------
    element: `xml.etree.ElementTree.Element`
        An XML element.
    namespace_dict: `Dict[str, str]`
        A namespace dictionary that allows module to parse FPDS elements.
    prefix: `str`
        Prefix to append to attribute dictionary. This will ensure that
        duplicate tags like `PIID` are distinguished in the data.
    """

    def __init__(self, prefix, *args, **kwargs) -> None:
        self.prefix = prefix
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:
        return f"<_ElementAttributes {self.tree.tag}>"

    def _generate_nested_attribute_dict(self) -> Dict[str, str]:
        """Returns all attributes of an Element

        Example
        -------
        <ns1:contractActionType description="BPA" part8OrPart13="PART8">E</ns1:contractActionType>

        Extracting the text value from `contractActionType` would return "E".
        Addtional metadata is stored as tag attributes which this method will
        help parse out. This method will generate a dictionary including both
        the text and tag attribute data. In this example, `contractActionType`
        has two attributes: `description` and `part8OrPart13`. This method will
        represent this tag the following way:

            {
                "contractActionType": "E",
                "contractActionType__description": "BPA"
                "contractActionType__part8OrPart13": "PART8"
            }
        """
        attributes = self.tree.attrib
        _attributes_copy = attributes.copy()

        if self.tree.text:
            _attributes_copy[self.prefix] = self.tree.text
        for key in attributes:
            nested_key = f"{self.prefix}__{key}"
            _attributes_copy[nested_key] = attributes[key]
            del _attributes_copy[key]

        return _attributes_copy


class Entry(fpdsElement):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __call__(self):
        """Shortcut for the finalized data structure"""
        data_with_attributes = self.get_entry_data()
        data_with_attributes["award_type"] = self.contract_type
        return data_with_attributes

    @property
    def contract_type(self) -> str:
        """Added on v1.2.0

        Identifies the contract type for an individual award entry. Possible
        options include: `AWARD` or `IDV`
        """
        content = self.tree.find(".//ns0:content", self.namespace_dict)
        award = list(content)[0]
        award_type = re.sub(self.NAMESPACE_REGEX_PATTERN, "", award.tag)
        return award_type.upper()

    def parse_tags(self) -> Iterator[TREE]:
        """Returns iteration of `Element` as a generator"""
        return [tag for tag in self.tree.iter()]

    def get_entry_data(self) -> Dict[str, Union[str, int, float]]:
        entry_tags = dict()

        # for some reason, the tag we parse gets included in the final list
        tags = self.parse_tags()

        hierarchy = self.award_tag_hierarchy()
        # NOTE: remove indexing and remove item by value where clean_tag == "entry"
        for _tag in tags[1:]:
            prefix = hierarchy.get(_tag.tag)
            elem = _ElementAttributes(content=_tag, prefix=prefix)
            entry_tags.update(elem._generate_nested_attribute_dict())
        return entry_tags

    @property
    def tag_exclusions(self):
        """Tag names that should be excluded from the hierarchy tree. Because
        some of the XML hierarchy doesn't provide much value, we provide a
        mechanism for `award_tag_hierarchy` to avoid using such tags in the
        final string concatenation.
        """
        return ["content", "IDV", "award"]

    def award_tag_hierarchy(
        self,
        element: Element = None,
        parent: str = None,
        hierarchy: Dict = dict(),
        truncate: bool = True,  # to truncate hierarchy names
    ) -> Dict[str, str]:
        """Added on v1.2.0

        For each FPDS request made, the `entry` tag represents an individual
        award -- `AWARD` or `IDV`. The `content` tag contains a nested structure
        of tags with all relevant award metadata. In v1.0.0, this parser assumed
        each tag name to be unique, which caused duplicate tag names to be
        overwritten. In the example below, we can see two groupings of tags --
        `awardContractID` and `referencedIDVID` -- containing duplicate tag
        names `agencyID`, `PIID`, and `modNumber`. Because the referenced IDV tag
        succeeds the original award contract tag, only the referenced IDV data
        tags would exist in the final JSON structure. To ensure that we capture
        all data and correctly distinguish between an award PIID and referenced
        IDV PIID, this function will recursively parse through each entry's
        structure and generate a concatenated string of tag names.

        <content xmlns:ns1="https://www.fpds.gov/FPDS" type="application/xml">
            <ns1:awardID>
                <ns1:awardContractID>
                    <ns1:agencyID name="ENVIRONMENTAL PROTECTION AGENCY">6800</ns1:agencyID>
                    <ns1:PIID>0002</ns1:PIID>
                    <ns1:modNumber>P00018</ns1:modNumber>
                    <ns1:transactionNumber>0</ns1:transactionNumber>
                </ns1:awardContractID>
                <ns1:referencedIDVID>
                    <ns1:agencyID name="ENVIRONMENTAL PROTECTION AGENCY">6800</ns1:agencyID>
                    <ns1:PIID>EPS31703</ns1:PIID>
                    <ns1:modNumber>0</ns1:modNumber>
                </ns1:referencedIDVID>
            </ns1:awardID>
        </content>

        Parameters
        ----------
        element: `Element`
            Per docs, to get children simply iterate over element
            https://lxml.de/api/lxml.etree._Element-class.html#getchildren
        parent: `str`
            Name of `elements` XML parent
        hierarchy: `Dict[str, str]`
            The hierarchy dictionary structure to be passed through each
            recursive function call
        truncate: `bool`
            Should the tag hierarchy names be truncated?
        """
        if element is None:
            element = self.tree

        def shorten_parent_name(parent, delim="__"):
            """Shortens the parent name to take the outermost tag and the final
            tag name (which contains the actual data). Note: this function will
            only be used if `truncate` is set to `True`.
            """
            tags_split = parent.split(delim)
            if len(tags_split) > 2:
                abbreviated_name = tags_split[0] + "__" + tags_split[-1]
            else:
                abbreviated_name = "__".join(tags_split)
            return abbreviated_name

        children = list(element)
        if children:
            for child in children:
                # _tag = child.tag
                fpdsChild = fpdsElement(content=child)
                clean_tag = fpdsChild.clean_tag

                _parent = Parent(content=child, parent=parent)
                # if _parent.clean_tag not in self.tag_exclusions:
                parent_tag_name = (
                    f"{parent}__{clean_tag}"
                    if parent and parent not in self.tag_exclusions
                    else f"{clean_tag}"
                )
                # hierarchy[_tag] = parent_tag_name
                # parent_tag_name = _parent.parent_of_the_parent()
                hierarchy[_tag] = shorten_parent_name(parent_tag_name)
                # else:
                #     continue
                self.award_tag_hierarchy(
                    element=child, parent=parent_tag_name, hierarchy=hierarchy
                )
        return hierarchy


class Parent(Entry):
    """Identifies an xml tag as a parent. In this package, a parent tag
    is considered to have children elements.
    """

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    @property
    def parent_has_children(self):
        return bool(list(self.tree))

    def parent_of_the_parent(self, truncate=None):
        if self.parent:
            if self.clean_tag not in self.tag_exclusions:
                parent_hierarchy = f"{self.parent}__{self.clean_tag}"
            # if self.clean_tag in self.tag_exclusions:
            #      parent_hierarchy = EmptyParentName()
            # else:
            #     parent_hierarchy = f"{self.parent}__{self.clean_tag}"
        else:
            parent_hierarchy = f"{self.clean_tag}"

        return parent_hierarchy
