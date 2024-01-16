"""
XML classes for parsing FPDS content.

author: derek663@gmail.com
last_updated: 01/15/2024
"""
import re
from typing import Dict, Iterator, List, Optional, Union
from xml.etree.ElementTree import Element, ElementTree, fromstring

from fpds.core import FPDS_ENTRY
from fpds.core.mixins import fpdsMixin, fpdsXMLMixin

NAMESPACE_REGEX = r"\{(.*)\}"
LAST_PAGE_REGEX = r"start=(.*?)$"


class fpdsXML(fpdsXMLMixin, fpdsMixin):
    """Parses FPDS request content received as bytes or `ElementTree`.
    This class represents an entire XML document.

    Parameters
    ----------
    content: `Union[bytes, ElementTree]`
        Bytes content or an `ElementTree` type that can be parsed into
        valid XML.

    Raises
    ------
    TypeError:
        If `content` is not of type `bytes` or an instance of `ElementTree`.
    """

    def __init__(self, content: Union[bytes, ElementTree]) -> None:
        if isinstance(content, bytes):
            self.content = content
            self.tree = self.convert_to_lxml_tree()
        if isinstance(content, self.xml_child_classes):
            self.tree = content
        if not isinstance(content, self.xml_child_classes + (bytes,)):
            module_names = ",".join(
                [f"`{mod}`" for mod in self.xml_child_classes_with_modules]
            )
            raise TypeError(
                f"You must provide bytes content or an instance of the "
                f"following: {module_names}."
            )

    def __str__(self) -> str:
        """The root represents the top of the XML tree from an instance of type
        `ElementTree`. Since `fpdsElement` inherits from this class, we overwrite
        this method in child classes since `getroot()` is not available for
        tags of type `Element`
        """
        if isinstance(self.tree, ElementTree):
            root = self.tree.getroot()
            query = root.find(".//ns0:title", self.namespace_dict)
            assert isinstance(query, Element)

            page = root.find(".ns0:link[@rel='alternate']", self.namespace_dict)
            assert isinstance(page, Element)

            return f"<fpdsXML query=`{query.text}` page=`{page.attrib['href']}`>"

    def parse_items(self) -> Iterator[Element]:
        """Returns iteration of `Element` as a generator"""
        yield from self.tree.iter()

    def convert_to_lxml_tree(self) -> ElementTree:
        """Returns an `ElementTree` object from a bytes response"""
        tree = ElementTree(fromstring(self.content))
        return tree

    @staticmethod
    def _get_full_namespace(element: Element) -> str:
        """For some odd reason, the `xml` API doesn't have a method to provide
        namespaces natively unless an XML file is saved locally. To avoid this,
        we just do some regex work.

        Parameters
        ----------
        element: `Element`
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
        for element in self.parse_items():
            _namespace = self._get_full_namespace(element)
            if _namespace not in namespaces:
                namespaces.append(_namespace)

        namespace_dict = {f"ns{idx}": ns for idx, ns in enumerate(namespaces)}
        return namespace_dict

    @property
    def total_record_count(self) -> int:
        """Total number of records across all pagination links."""
        last_link = self.tree.find(".//ns0:link[@rel='last']", self.namespace_dict)
        if isinstance(last_link, Element):
            # length of last_link should always be 1
            match = re.search(LAST_PAGE_REGEX, last_link.attrib["href"])
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
        offset = 0 if self.total_record_count < 10 else resp_size
        page_range = list(range(0, self.total_record_count + offset, resp_size))
        page_links = []
        for num in page_range:
            link = f"{self.url_base}&q={params}&start={num}"
            page_links.append(link)
        return page_links

    def get_atom_feed_entries(self) -> List[Element]:
        """Returns tree entries that contain FPDS record data"""
        data_entries = self.tree.findall(".//ns0:entry", self.namespace_dict)
        return data_entries

    def jsonified_entries(self) -> List[FPDS_ENTRY]:
        """Returns all paginated entries from an FPDS request"""
        entries = self.get_atom_feed_entries()
        json_data = [Entry(content=entry)() for entry in entries]
        return json_data


class fpdsElement(fpdsXML):
    """Representation of a single FPDS XML element. This utility class helps us
    retrieve the name of XML tags without the namespace.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # per the `xml` API, an `ElementTree` and `Element` are different
        # we ensure we follow that convention here by removing the `tree` attrib
        self.element = self.tree
        delattr(self, "tree")

    def __str__(self) -> str:
        return f"<fpdsElement {self.tag}>"

    def parse_items(self) -> Iterator[Element]:
        """Returns iteration of `Element` as a generator"""
        yield from self.element.iter()

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
    def tag(self):
        """Raw tag from `xml` library"""
        return self.element.tag

    @property
    def clean_tag(self) -> str:
        """Tag name without the namespace. A tag like the following:
        `ns1:productOrServiceInformation` would simply return
        `productOrServiceInformation`
        """
        clean_tag = re.sub(self.NAMESPACE_REGEX_PATTERN, "", self.tag)
        return clean_tag


class _ElementAttributes(fpdsElement, fpdsXMLMixin):
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

    def __init__(self, prefix: str, *args, **kwargs) -> None:
        self.prefix = prefix
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:   # pragma: no cover
        return f"<_ElementAttributes {self.tag}>"

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
                "{prefix}__contractActionType": "E",
                "{prefix}__contractActionType__description": "BPA"
                "{prefix}__contractActionType__part8OrPart13": "PART8"
            }
        """
        assert isinstance(self.element, Element)

        attributes = self.element.attrib
        _attributes_copy = attributes.copy()

        if self.element.text:
            _attributes_copy[self.prefix] = self.element.text
        for key in attributes:
            nested_key = f"{self.prefix}__{key}"
            _attributes_copy[nested_key] = attributes[key]
            del _attributes_copy[key]

        return _attributes_copy


class Entry(fpdsElement):
    """New as of v1.2.0

    Representation of a single FPDS award item. In terms of XML, it is the
    outermost container for award data. Each entry contains four children tags --
    `title`, `link`, `modified`, and `content`. The `content` tag will contain
    the bulk of data to be extracted, but tags like `title` and `modified`
    also contain useful info.

    Example:
    --------

     <entry>
        <title>
            <![CDATA[PURCHASE ORDER 1B3G02670 (PA09) awarded to MC ALLEN CITY OF, was modified for the amount of $8,392.9]]>
        </title>
        <link rel="alternate" type="text/html" href="https://www.fpds.gov/ezsearch/search.do?s=FPDS&amp;indexName=awardfull&amp;templateName=1.5.3&amp;q=1B3G02670+4740+"></link>
        <modified>2013-12-18 17:03:03</modified>
        <content xmlns:ns1="https://www.fpds.gov/FPDS" type="application/xml">
            <ns1:award xmlns:ns1="https://www.fpds.gov/FPDS" version="1.4">
                <ns1:awardID>
                    <ns1:awardContractID>
                        <ns1:agencyID name="PUBLIC BUILDINGS SERVICE">4740</ns1:agencyID>
    </entry>
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __str__(self) -> str:   # pragma: no cover
        return f"<Entry {self.clean_tag}>"

    def __call__(self) -> FPDS_ENTRY:
        """Shortcut for the finalized data structure"""
        data_with_attributes = self.get_entry_data()
        return data_with_attributes

    @property
    def contract_type(self) -> str:
        """Identifies the contract type for an individual award entry. Possible
        options include: `AWARD` or `IDV`
        """
        content = self.element.find(".//ns0:content", self.namespace_dict)
        if content:
            award = list(content)[0]
            award_type = re.sub(self.NAMESPACE_REGEX_PATTERN, "", award.tag)
        return award_type.upper()

    def get_entry_data(self) -> Dict[str, str]:
        """Extracts award data from an entry"""
        entry_tags = dict()  # type: Dict[str, str]
        hierarchy = self.content_tag_hierarchy()

        for prefix, tag in hierarchy.items():
            attributes = _ElementAttributes(content=tag, prefix=prefix)
            entry_tags.update(attributes._generate_nested_attribute_dict())
            # the dumbest part of this data is it not natively having a column
            # for the contract type
            entry_tags["contract_type"] = self.contract_type
        return entry_tags

    def content_tag_hierarchy(
        self,
        element: Optional[Element] = None,
        parent: Optional[str] = None,
        hierarchy: Dict[str, str] = dict(),
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
        element: `Optional[Element]`
            Per docs, to get children simply iterate over element
            https://lxml.de/api/lxml.etree._Element-class.html#getchildren
        parent: `Optional[str]`
            Name of `elements` XML parent
        hierarchy: `Dict[str, str]`
            The hierarchy dictionary structure to be passed through each
            recursive function call
        """
        if element is None:
            element = self.element  # type: ignore

        _parent = Parent(content=element)

        # continue parsing XML hierarchy because children exist and we want
        # to get every possible bit of data
        if _parent.children():
            for child in _parent.children():
                _child = Parent(content=child, parent_name=parent)
                parent_tag_name = _child.parent_child_hierarchy_name()
                hierarchy[parent_tag_name] = child
                self.content_tag_hierarchy(
                    element=child, parent=parent_tag_name, hierarchy=hierarchy
                )
        return hierarchy


class Parent(fpdsElement):
    """Identifies an xml tag as a parent. In this package, a parent tag
    is considered to have children elements.
    """

    def __init__(self, parent_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_name = parent_name

    @property
    def tag_exclusions(self) -> List[str]:
        """Tag names that should be excluded from the hierarchy tree. Because
        some of the XML hierarchy doesn't provide much value, we provide a
        mechanism for `award_tag_hierarchy` to avoid using such tags in the
        final string concatenation.
        """
        return ["content", "IDV", "award"]

    def children(self):
        """Returns children if they exist"""
        if self.element.getchildren():
            return self.element.getchildren()

    def parent_child_hierarchy_name(self, delim="__"):
        if self.parent_name and self.parent_name not in self.tag_exclusions:
            name = self.parent_name + delim + self.clean_tag
        else:
            name = self.clean_tag
        return name
