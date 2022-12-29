import pytest
import unittest
from unittest import TestCase, mock
from xml.etree import ElementTree

import requests

from fpds import fpdsRequest
from tests import FULL_RESPONSE_DATA_BYTES

# valid params and values
FPDS_REQUEST_PARAMS_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "7504",
}
# an invalid param combined with a valid param
FPDS_REQUEST_INVALID_PARAM_DICT = {
    "INCORRECT_PARAM": "some-value",
    "AGENCY_CODE": "7504",
}
# valid param names, but an incorrect regex pattern for a single param
FPDS_REQUEST_INVALID_REGEX_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "not-a-proper-regex",
}
CONTENT_TREE = ElementTree.fromstring(FULL_RESPONSE_DATA_BYTES)


class MockResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code

    @property
    def content(self):
        return FULL_RESPONSE_DATA_BYTES

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception


class MockFpdsXML(object):
    def pagination_links(self, params="some-param1: param1-value"):
        return [
            "{some-fpds-link}&start=0",
            "{some-fpds-link}&start=10",
            "{some-fpds-link}&start=20",
        ]


class TestFpdsRequest(TestCase):
    def setUp(self):
        self._class = fpdsRequest(**FPDS_REQUEST_PARAMS_DICT)

    def test_params_exist(self):
        with pytest.raises(ValueError):
            fpdsRequest({})

    def test_invalid_param(self):
        with pytest.raises(ValueError):
            fpdsRequest(**FPDS_REQUEST_INVALID_PARAM_DICT)

    def test_invalid_param_regex(self):
        with pytest.raises(ValueError):
            fpdsRequest(**FPDS_REQUEST_INVALID_REGEX_DICT)

    def test_str_magic_method(self):
        object_as_string = (
            "<fpdsRequest LAST_MOD_DATE=[2022/01/01, 2022/05/01] " 'AGENCY_CODE="7504">'
        )
        self.assertEqual(self._class.__str__(), object_as_string)

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
