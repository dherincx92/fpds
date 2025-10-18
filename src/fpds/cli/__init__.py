"""CLI namespace."""

import click

from .parse import parse as _parse
from .params import params as _params


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    CLI for parsing the FPDS ATOM feed found at
    https://www.fpds.gov/fpdsng_cms/index.php/en/
    """
    ascii_art = r"""
           __________  ____  _____
          / ____/ __ \/ __ \/ ___/
         / /_  / /_/ / / / /\__ \
        / __/ / ____/ /_/ /___/ /
       /_/   /_/   /_____//____/
    """
    click.echo(ascii_art + "\nWelcome to a more user-friendly FPDS 🚀\n")

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


cli.add_command(_parse)
cli.add_command(_params)
