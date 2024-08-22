import pytest
import unittest
import xml
from unittest import TestCase, mock
from xml.etree.ElementTree import ElementTree, fromstring

from fpds import fpdsRequest
from fpds.errors import (
    fpdsMismatchedParameterRegexError,
    fpdsInvalidParameter,
    fpdsMissingKeywordParameterError,
)
from tests import FULL_RESPONSE_DATA_BYTES

# valid params and values
FPDS_REQUEST_PARAMS_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "7504",
}

FPDS_SEARCH_PARAMS_PROPERTY = (
    "LAST_MOD_DATE:[2022/01/01, 2022/05/01] " 'AGENCY_CODE:"7504"'
)
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
CONTENT_TREE = ElementTree(fromstring(FULL_RESPONSE_DATA_BYTES))


class MockResponse(object):
    def __init__(self, status_code):
        self.status_code = status_code

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
        with pytest.raises(fpdsMissingKeywordParameterError):
            fpdsRequest({})

    def test_invalid_param(self):
        with pytest.raises(fpdsInvalidParameter):
            fpdsRequest(**FPDS_REQUEST_INVALID_PARAM_DICT)

    def test_invalid_param_regex(self):
        with pytest.raises(fpdsMismatchedParameterRegexError):
            fpdsRequest(**FPDS_REQUEST_INVALID_REGEX_DICT)

    def test_str_magic_method(self):
        object_as_string = (
            "<fpdsRequest LAST_MOD_DATE=[2022/01/01, 2022/05/01] " 'AGENCY_CODE="7504">'
        )
        self.assertEqual(self._class.__str__(), object_as_string)

    def test_search_params_property(self):
        self.assertEqual(FPDS_SEARCH_PARAMS_PROPERTY, self._class.search_params)

    @mock.patch.object(xml.etree.ElementTree, "fromstring")
    def test_convert_to_lxml_tree(self, mock_from_string):
        mock_from_string.return_value = ElementTree(
            fromstring(FULL_RESPONSE_DATA_BYTES)
        )
        tree = self._class.convert_to_lxml_tree(content=FULL_RESPONSE_DATA_BYTES)
        self.assertIsInstance(tree, ElementTree)


if __name__ == "__main__":
    unittest.main()
