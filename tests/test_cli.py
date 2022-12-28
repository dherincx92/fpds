import unittest
from unittest import TestCase

from click.testing import CliRunner
from fpds.cli import cli

invalid_cli_params = ['parse', 'params', "{an-invalid-param}={some-value}"]
invalid_cli_param_regex = ['parse', 'params', 'AGENCY_CODE={not-valid}']


class TestFpdsCLI(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_missing_cli_parameters(self):
        result = self.runner.invoke(cli, ['parse'])
        assert "Please provide at least one parameter" in result.output

    def test_invalid_cli_parameter(self):
        result = self.runner.invoke(cli, invalid_cli_params)
        assert "is not a valid parameter" in result.output

    def test_invalid_cli_parameter_regex_pattern(self):
        result = self.runner.invoke(cli, invalid_cli_param_regex)
        assert "does not match regex" in result.output


if __name__ == "__main__":
    unittest.main()
