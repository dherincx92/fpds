import sys

from tests.utilities import read_xml_as_bytes

FPDS_TEST_PACKAGE = "tests.data"

if sys.version_info[1] <= 8:
    from importlib.resources import path

    with path(FPDS_TEST_PACKAGE, "full_response.xml") as file:
        FPDS_XML_TEST_DATA_FILE = file

    with path(FPDS_TEST_PACKAGE, "truncated_response.xml") as file:
        FPDS_TRUNCATED_XML_TEST_DATA_FILE = file
else:
    from importlib.resources import files

    FPDS_XML_TEST_DATA_FILE = files(FPDS_TEST_PACKAGE).joinpath("full_response.xml")
    FPDS_TRUNCATED_XML_TEST_DATA_FILE = files(FPDS_TEST_PACKAGE).joinpath(
        "truncated_response.xml"
    )

# XML sample responses
FULL_RESPONSE_DATA_BYTES = read_xml_as_bytes(FPDS_XML_TEST_DATA_FILE)
TRUNCATED_RESPONSE_DATA_BYTES = read_xml_as_bytes(FPDS_TRUNCATED_XML_TEST_DATA_FILE)
