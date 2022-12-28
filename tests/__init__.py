from importlib.resources import files

from tests.utilities import read_xml_as_bytes

FPDS_TEST_DATA_DIR = "tests.data"
FPDS_XML_TEST_DATA_FILE = files(FPDS_TEST_DATA_DIR).joinpath("full_response.xml")
FPDS_TRUNCATED_XML_TEST_DATA_FILE = files(FPDS_TEST_DATA_DIR).joinpath("truncated_response.xml")

# XML sample responses
FULL_DATA_BYTES = read_xml_as_bytes(FPDS_XML_TEST_DATA_FILE)
TRUNCATED_DATA_BYTES = read_xml_as_bytes(FPDS_TRUNCATED_XML_TEST_DATA_FILE)