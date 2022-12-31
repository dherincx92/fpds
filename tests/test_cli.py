import unittest
from unittest import TestCase

from click.testing import CliRunner
from fpds.cli import cli


class TestFpdsCLI(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_missing_cli_parameters(self):
        result = self.runner.invoke(cli, ["parse"])
        assert "Please provide at least one parameter" in result.output

    def test_invalid_cli_parameter(self):
        result = self.runner.invoke(cli, ["parse", "{an-invalid-param}={some-value}"])
        assert "is not a valid parameter" in result.output

    def test_invalid_cli_parameter_regex_pattern(self):
        result = self.runner.invoke(cli, ["parse", "AGENCY_CODE={not-valid}"])
        assert "does not match regex" in result.output


if __name__ == "__main__":
    unittest.main()
