import unittest
from unittest import TestCase, mock
from xml.etree.ElementTree import ElementTree, fromstring

from fpds import fpdsRequest
from fpds.errors import (
    fpdsInvalidParameter,
    fpdsMaxPageLengthExceededError,
    fpdsMismatchedParameterRegexError,
    fpdsMissingKeywordParameterError,
)
from tests import FULL_RESPONSE_DATA_BYTES

# valid params and values
FPDS_REQUEST_PARAMS_DICT = {
    "LAST_MOD_DATE": "[2022/01/01, 2022/05/01]",
    "AGENCY_CODE": "7504",
}

FPDS_SEARCH_PARAMS_PROPERTY = (
    'LAST_MOD_DATE:[2022/01/01, 2022/05/01] AGENCY_CODE:"7504"'
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


class MockHTTPResponse:
    def read(self):
        return FULL_RESPONSE_DATA_BYTES

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class MockFpdsXML(object):
    def pagination_links(self, params="some-param1: param1-value"):
        return [
            "{some-fpds-link}&start=0",
            "{some-fpds-link}&start=10",
            "{some-fpds-link}&start=20",
        ]


class TestFpdsRequest(TestCase):
    def test_params_exist(self):
        with self.assertRaises(fpdsMissingKeywordParameterError):
            fpdsRequest({})

    @mock.patch("fpds.core.parser.urlopen")
    def test_request_link_count(self, mock_urlopen):
        """Test that generated number of links from initial request is correct."""
        mock_urlopen.return_value = MockHTTPResponse()
        req = fpdsRequest(**FPDS_REQUEST_PARAMS_DICT)
        self.assertEqual(len(req.links), 3)

    @mock.patch("fpds.core.parser.fpdsRequest.page_index")
    @mock.patch("fpds.core.parser.urlopen")
    def test_request_link_count(self, mock_urlopen, mock_page_index):
        """Test that page_index is called once when page is provided."""
        mock_urlopen.return_value = MockHTTPResponse()
        fpdsRequest(
            **FPDS_REQUEST_PARAMS_DICT,
            page=1,
        )
        mock_page_index.assert_called_once()

    @mock.patch("fpds.core.parser.urlopen")
    def test_max_page_length_exceeded_error_raised(self, mock_urlopen):
        mock_urlopen.return_value = MockHTTPResponse()
        with self.assertRaises(fpdsMaxPageLengthExceededError):
            fpdsRequest(
                **FPDS_REQUEST_PARAMS_DICT,
                page=1_000_000,
            )

    @mock.patch("fpds.core.parser.urlopen")
    def test_skip_regex_validation_warning_raised(self, mock_urlopen):
        mock_urlopen.return_value = MockHTTPResponse()
        with self.assertWarns(UserWarning):
            fpdsRequest(
                **FPDS_REQUEST_PARAMS_DICT,
                skip_regex_validation=True,
            )


if __name__ == "__main__":
    unittest.main()
