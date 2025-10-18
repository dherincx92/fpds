"""
Command for displaying FPDS filtering fields.

author: derek663@gmail.com
last_updated: 2025-10-18
"""

import click
import json
import textwrap

from fpds.config import FPDS_DATA_DIR, FPDS_FIELDS_CONFIG
from tabulate import tabulate


@click.option(
    "-e",
    "--export",
    required=False,
    type=bool,
    help="If True, exports full list of field metadata",
)
@click.command()
def fields(export):
    """
    Command for displaying available filtering fields for the parsing command.

    \b
    Usage:
        $ fpds fields [OPTIONS]

    \b
    Options:
        -e, --export  If True, exports all available metadata for fields.
    """
    parameters = FPDS_FIELDS_CONFIG

    if export:
        metadata_file = FPDS_DATA_DIR / "fields.json"
        with open(metadata_file, "w") as f:
            json.dump(parameters, f)
        click.echo(click.style(f"Fields metadata exported to {metadata_file}", fg="green"))
        return

    message = (
        f"The following {len(parameters)} fields support regex validation. "
        "If you wish to see more details about fields, set the --export flag to True. "
        "If your field is not listed or if the regex pattern is no longer valid, "
        "bypass validation by using the --skip-regex-validation flag. "
        "Consult the README.md for examples."
    )
    click.echo(click.style("\n".join(textwrap.wrap(message, width=87)), fg="green"))
    data = [[field['name'], field['description']] for field in FPDS_FIELDS_CONFIG]
    headers = ["Name", "Description"]
    click.echo(tabulate(data, headers=headers, tablefmt="fancy_grid"))
