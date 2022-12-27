import pytest
import unittest
from unittest import TestCase
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from fpds import fpdsXML
from fpds.config import FPDS_XML_TEST_DATA_FILE as TEST_FILE

FPDS_REQUEST_PARAMS_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "7504"
}

with open(TEST_FILE) as data:
    DATA_BYTES = data.read().encode("utf-8")

CONTENT_TREE = ElementTree.fromstring(DATA_BYTES)
TEST_NAMESPACE_DICT = {
    'ns0': 'http://www.w3.org/2005/Atom',
    'ns1': 'https://www.fpds.gov/FPDS'
}


class TestFpdsXML(TestCase):
    def setUp(self):
        self._class = fpdsXML(DATA_BYTES)

    def test_invalid_content_type(self):
        with pytest.raises(TypeError):
            fpdsXML(content="a-string-not-bytes-or-tree")

    def test_convert_to_lxml_tree(self):
        content = self._class.convert_to_lxml_tree()
        self.assertIsInstance(content, Element)

    def test_response_size(self):
        self.assertEqual(self._class.response_size, 10)

    def test_namespace_dict(self):
        namespace_dict = self._class.namespace_dict
        self.assertEqual(namespace_dict, TEST_NAMESPACE_DICT)

    def test_total_record_count(self):
        total = self._class.total_record_count
        self.assertEqual(total, 20)

    def test_get_atom_feed_entries(self):
        entries = self._class.get_atom_feed_entries()
        # all entries should be of the same type
        entry_types = set([type(entry) for entry in entries])
        self.assertEqual(len(entries), 10)
        self.assertEqual(len(entry_types), 1)

