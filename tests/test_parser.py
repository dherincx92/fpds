import asyncio
import unittest
from unittest import TestCase, mock
from xml.etree.ElementTree import ElementTree, fromstring

from fpds import fpdsRequest
from fpds.core.xml import fpdsSubTree
from fpds.errors import (
    fpdsDuplicateParameterConfiguration,
    fpdsInvalidParameter,
    fpdsMaxPageLengthExceededError,
    fpdsMismatchedParameterRegexError,
    fpdsMissingKeywordParameterError,
)
from tests import FULL_RESPONSE_DATA_BYTES, NO_LINK_RESPONSE_DATA_BYTES

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
    def __init__(self, content: bytes = FULL_RESPONSE_DATA_BYTES):
        self.content = content

    def read(self):
        return self.content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class TestFpdsRequest(TestCase):
    def test_parameter_error_raised_with_no_kwargs(self):
        with self.assertRaises(fpdsMissingKeywordParameterError):
            fpdsRequest({})

    @mock.patch("fpds.core.parser.urlopen")
    def test_mb_to_bytes(self, mock_urlopen):
        """Test that mb_to_bytes correctly converts megabytes to bytes."""
        mock_urlopen.return_value = MockHTTPResponse()
        req = fpdsRequest(**FPDS_REQUEST_PARAMS_DICT, max_chunk_size_mb=50)
        self.assertEqual(req.mb_to_bytes(), 50 * 1_048_576)

    @mock.patch("fpds.core.parser.urlopen")
    def test_no_pagination_links(self, mock_urlopen):
        """Test that initial_request correctly returns the root XML tree from the initial request."""
        mock_urlopen.return_value = MockHTTPResponse(
            content=NO_LINK_RESPONSE_DATA_BYTES
        )
        req = fpdsRequest(**FPDS_REQUEST_PARAMS_DICT)
        self.assertEqual(asyncio.run(req.fetch()), [])

    # @mock.patch("fpds.core.parser.urlopen")
    # def test_convert(self, mock_urlopen):
    #     """Test that initial_request correctly returns the root XML tree from the initial request."""
    #     mock_urlopen.return_value = MockHTTPResponse()
    #     req = fpdsRequest(**FPDS_REQUEST_PARAMS_DICT)
    #     mock_client = mock.AsyncMock()
    #     mock_client.get.return_value = MockHTTPResponse(content=FULL_RESPONSE_DATA_BYTES)

    #     from asyncio import Semaphore
    #     semaphore = Semaphore(10)
    #     result = asyncio.run(
    #         req.convert(
    #             client=mock_client,
    #             link="https://example.com/fpds",
    #             semaphore=semaphore,
    #         )
    #     )

    #     # Assertions
    #     self.assertIsInstance(result, fpdsSubTree)

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
