"""
Parsing command for retrieving FPDS federal
contracts.

author: derek663@gmail.com
last_updated: 2025-07-14
"""

import asyncio
import json
from pathlib import Path
from uuid import uuid4

import click
from click import UsageError

from fpds import fpdsRequest
from fpds.config import FPDS_DATA_DATE_DIR
from fpds.utilities import validate_kwarg


@click.command()
@click.option(
    "-k",
    "--skip-regex-validation",
    metavar="<bool>",
    required=False,
    default=False,
    type=bool,
    help="If True, skips param regex validation",
)
@click.option(
    "-o",
    "--output-dir",
    required=False,
    metavar="<string>",
    type=click.Path(exists=False, path_type=Path),
    help="Output directory",
)
@click.argument("params", nargs=-1)
def parse(params, output_dir, skip_regex_validation) -> None:  # type: ignore
    """
    Parsing command for the FPDS Atom feed

    \b
    Usage:
        $ fpds parse [PARAMS] [OPTIONS]

    \b
    Positional Argument(s):
        PARAMS  Search criteria parameters for filtering response

        \b
        Reference the Atom Feed Usage documentation at
        https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage
        to determine available parameters. As an example, if
        a user wants to filter for AWARD contract types, the
        parameter criteria should look like this: 'CONTRACT_TYPE=AWARD'.
        A full CLI command could look like this:

        \b
          fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
    """

    if output_dir:
        if not output_dir.exists():
            click.echo(f"Creating output directory {str(output_dir.resolve())}")
            output_dir.mkdir(parents=True, exist_ok=True)

    params = [param.split("=") for param in params]

    if not params:
        raise UsageError("Please provide at least one parameter")

    for _param in params:  # _param is a tuple
        name, value = _param
        _param[1] = validate_kwarg(kwarg=name, string=value)

    params_kwargs = dict(params)
    click.echo(f"Params to be used for FPDS search: {params_kwargs}")

    request = fpdsRequest(**params_kwargs, cli_run=True, skip_regex_validation=skip_regex_validation)
    click.echo("Retrieving FPDS records from ATOM feed...")

    records = asyncio.run(request.data())
    DATA_DIR = output_dir if output_dir else FPDS_DATA_DATE_DIR
    DATA_FILE = DATA_DIR / f"{uuid4()}.json"
    with open(DATA_FILE, "w") as outfile:
        json.dump(records, outfile)

    click.echo(f"{len(records)} record(s) have been saved as JSON at: {DATA_FILE}")
