import click
from click import Argument, Choice, Path, UsageError


@click.command()
@click.argument("params", nargs=-1)
def parse(params):
    """
    Parsing command to retrieve results from the FPDS ATOM feed
    \b
    Usage:
        $ fpds parse [PARAMS]
    \b
    Positional Argument(s):
        PARAMS  Search criteria parameters for filtering response

        Reference the Atom Feed Usage documentation at
        https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage to determine
        how to format parameters for the CLI. As an example, if a user
        wants to filter for AWARD contract types, the parameter criteria
        should look like this: `'CONTRACT_TYPE=”AWARD”'`. All parameter
        strings should be surrounded by single quotes to protect against
        errors where the value of the parameter is a string like the
        example above. A full cli command could look like this:
        `fpds parse params "LAST_MODE_DATE=[2022/01/01, 2022/05/01]" "AGENCY_CODE=7504"
    """
    params = [param.split("=") for param in params[1:]]
    params_kwargs = dict(params)
    

    click.echo(params_kwargs)
