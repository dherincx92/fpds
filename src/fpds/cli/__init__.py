import click

from .fpds import parse as _parse


@click.group()
def cli():
    """
    CLI for parsing the FPDS ATOM feed found at
    https://www.fpds.gov/fpdsng_cms/index.php/en/
    """


cli.add_command(_parse)