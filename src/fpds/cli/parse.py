"""
Parsing command for retrieving FPDS federal
contracts

author: derek663@gmail.com
last_updated: 12/30/2022
"""
import json
from pathlib import Path
from uuid import uuid4

import click
from click import UsageError

from fpds import fpdsRequest
from fpds.config import FPDS_DATA_DATE_DIR
from fpds.config import FPDS_FIELDS_CONFIG as FIELDS
from fpds.utilities import validate_kwarg


@click.command()
@click.option("-o", "--output", required=False, help="Output directory")
@click.argument("params", nargs=-1)
def parse(params, output):
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

    if output:
        OUTPUT_PATH = Path(output)
        if not OUTPUT_PATH.exists():
            click.echo(f"Creating output directory {str(OUTPUT_PATH.resolve())}")
            OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

    params = [param.split("=") for param in params]
    field_names = [field.get("name") for field in FIELDS]

    if not params:
        raise UsageError("Please provide at least one parameter")

    for _param in params:   # _param is a tuple
        name, value = _param
        _param[1] = validate_kwarg(kwarg=name, string=value)

    params_kwargs = dict(params)
    click.echo(f"Params to be used for FPDS search: {params_kwargs}")

    request = fpdsRequest(**params_kwargs, cli_run=True)
    click.echo("Retrieving FPDS records from ATOM feed...")
    records = request()

    DATA_DIR = OUTPUT_PATH if output else FPDS_DATA_DATE_DIR
    DATA_FILE = DATA_DIR / f"{uuid4()}.json"
    with open(DATA_FILE, "w") as outfile:
        json.dump(records, outfile)

    click.echo(f"{len(records)} records have been saved as JSON at: {DATA_FILE}")
