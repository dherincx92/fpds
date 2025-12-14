import unittest
from unittest import TestCase

from typer.testing import CliRunner

from fpds.cli import app


class TestFpdsCLI(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_assert_required_params_with_parse_command(self):
        result = self.runner.invoke(app, ["parse"])
        print(result.output)
        self.assertIn("Missing argument", result.output)

    def test_invalid_cli_parameter(self):
        result = self.runner.invoke(app, ["parse", "FAKE_PARAM=FAKE_VALUE"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("not a valid FPDS parameter", result.__str__())

    def test_invalid_cli_parameter_regex_pattern(self):
        result = self.runner.invoke(app, ["parse", "AGENCY_CODE={not-valid}"])
        self.assertIn("does not match regex", result.__str__())

    def test_parse_with_custom_output_dir(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(
                app,
                [
                    "parse",
                    "AGENCY_CODE=7504",
                    "-o",
                    "./test",
                ],
            )
            self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
