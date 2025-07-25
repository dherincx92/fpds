from unittest import TestCase
from xml.etree.ElementTree import ElementTree

from fpds.core.xml import fpdsElement, fpdsTree
from tests import FULL_RESPONSE_DATA_BYTES, TRUNCATED_RESPONSE_DATA_BYTES

FPDS_REQUEST_PARAMS_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "7504",
}
TEST_NAMESPACE_DICT = {
    "ns0": "http://www.w3.org/2005/Atom",
    "ns1": "https://www.fpds.gov/FPDS",
}


class TestFpdsTree(TestCase):
    def setUp(self):
        self._class = fpdsTree(FULL_RESPONSE_DATA_BYTES)

    def test_convert_to_lxml_tree(self):
        content = self._class.convert_to_lxml_tree()
        self.assertIsInstance(content, ElementTree)

    def test_response_size(self):
        self.assertEqual(self._class.response_size, 10)

    def test_namespace_dict(self):
        namespace_dict = self._class.namespace_dict
        self.assertEqual(namespace_dict, TEST_NAMESPACE_DICT)

    def test_lower_limit(self):
        total = self._class.lower_limit
        self.assertEqual(total, 20)

    def test_lower_limit_count_truncated_response(self):
        """A truncated response won't have a `last` link tag. This test
        ensures that if the response size is less than 10 that the
        `lower_limit` property is still generated correctly.
        """
        _class = fpdsTree(TRUNCATED_RESPONSE_DATA_BYTES)
        total = _class.lower_limit
        self.assertEqual(total, 1)

    def test_pagination_links(self):
        links = self._class.pagination_links(params="some-param1: param1-value")
        self.assertEqual(len(links), 3)

    def test_get_atom_feed_entries(self):
        entries = self._class.get_atom_feed_entries()
        # all entries should be of the same type
        entry_types = set([type(entry) for entry in entries])
        self.assertEqual(len(entry_types), 1)

    def test_jsonify(self):
        entries = self._class.jsonify()
        self.assertEqual(len(entries), 10)


class TestFpdsElement(TestCase):
    def setUp(self):
        xml = fpdsTree(content=FULL_RESPONSE_DATA_BYTES)
        element = xml.get_atom_feed_entries()[0]
        self._class = fpdsElement(content=element)
