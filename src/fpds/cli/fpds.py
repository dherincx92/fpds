import json
import re
from uuid import uuid4

import click
from click import UsageError, BadArgumentUsage, BadParameter

from fpds import fpdsRequest, FPDS_DATA_DATE_DIR
from fpds.config import FPDS_FIELDS_CONFIG as FIELDS
from fpds.utilities import filter_config_dict, raw_literal_regex_match

@click.command()
@click.argument("params", nargs=-1)
def parse(params):
    """
    Parsing command to parse the FPDS Atom feed

    \b
    Usage:
        $ fpds parse [PARAMS]

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
            fpds parse params "LAST_MOD_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
    """
    params = [param.split("=") for param in params[1:]]
    field_names = [field.get("name") for field in FIELDS]

    if not params:
        raise UsageError("Please provide at least one parameter")

    for param_tuple in params:
        # checks that every parameter provided is valid
        param_name, param_input = param_tuple
        if param_name not in field_names:
            raise BadParameter(
                message=f"`{param_name}` is not a valid parameter"
            )

        kwarg_dict = filter_config_dict(FIELDS, "name", param_name)
        kwarg_regex = kwarg_dict.get("regex")
        match = raw_literal_regex_match(kwarg_regex, param_input)
        if not match:
            raise BadArgumentUsage(
                message=f"`{param_input}` does not match regex: {kwarg_regex}"
            )

        # enclose param value in quotes, if required by the Atom feed
        if kwarg_dict.get("quotes"):
            param_tuple[1] = f'"{param_input}"'

    params_kwargs = dict(params)
    click.echo(f"Params to be used for FPDS search: {params_kwargs}")

    request = fpdsRequest(**params_kwargs, cli_run=True)
    click.echo("Retrieving FPDS records from ATOM feed...")
    records = request()

    DATA_FILE = FPDS_DATA_DATE_DIR / f"{uuid4()}.json"
    with open(DATA_FILE, "w") as outfile:
        json.dump(records, outfile)

    click.echo(f"{len(records)} records have been dumped into JSON")
