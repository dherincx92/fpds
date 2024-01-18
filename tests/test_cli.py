import unittest
from unittest import TestCase

from click.testing import CliRunner
from fpds.cli import cli


class TestFpdsCLI(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_missing_cli_parameters(self):
        result = self.runner.invoke(cli, ["parse"])
        self.assertIn("Please provide at least one parameter", result.output)

    def test_invalid_cli_parameter(self):
        result = self.runner.invoke(cli, ["parse", "{an-invalid-param}={some-value}"])
        self.assertIn("is not a valid FPDS parameter", result.__str__())

    def test_invalid_cli_parameter_regex_pattern(self):
        result = self.runner.invoke(cli, ["parse", "AGENCY_CODE={not-valid}"])
        self.assertIn("does not match regex", result.__str__())


if __name__ == "__main__":
    unittest.main()
