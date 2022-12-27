import unittest
from unittest import TestCase, mock
from unittest.mock import MagicMock
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests

from fpds import fpdsRequest

FPDS_REQUEST_PARAMS_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "7504"
}

FILE = "/Users/dherincx/projects/git/fpds/src/fpds/tests/test_data.xml"
with open(FILE) as data:
    DATA_BYTES = data.read().encode("utf-8")

CONTENT_TREE = ElementTree.fromstring(DATA_BYTES)


class MockResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code

    @property
    def content(self):
        return DATA_BYTES

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception


class MockFpdsXML(object):
    def pagination_links(self, params="some-param1: param1-value"):
        return [
            '{some-fpds-link}&start=0',
            '{some-fpds-link}&start=10',
            '{some-fpds-link}&start=20'
        ]


class TestFpdsRequest(TestCase):
    def setUp(self):
        self._class = fpdsRequest(**FPDS_REQUEST_PARAMS_DICT)

    @mock.patch.object(requests, "get")
    def test_send_request(self, mock_response):
        mock_response.return_value = MockResponse(status_code=200)
        self._class.send_request()
        self.assertIn("content", self._class.__dict__)

    @mock.patch.object(fpdsRequest, "send_request")
    @mock.patch("fpds.core.parser.fpdsXML")
    def test_create_content_iterable(self, mock_xml, mock_response):
        self._class.content = [CONTENT_TREE]
        mock_xml.return_value = MockFpdsXML()
        mock_response.return_value = MockResponse(status_code=200)
        self._class.create_content_iterable()
        self.assertEqual(mock_response.call_count, 3)

    def side_effect_create_content_iterable(self):
        self._class.content.append(CONTENT_TREE)

    @mock.patch.object(fpdsRequest, "create_content_iterable")
    def test_parse_content(self, mock_content):
        mock_content.side_effect = self.side_effect_create_content_iterable()
        records = self._class.parse_content()
        self.assertEqual(len(records), 10)

if __name__ == "__main__":
    unittest.main()
