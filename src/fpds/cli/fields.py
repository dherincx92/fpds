"""CLI command for listing available fitering fields.

author: derek663@gmail.com
last_updated: 2025-12-14
"""

import re
import textwrap

import typer
from typing import Optional
from tabulate import tabulate
from typing_extensions import Annotated

from fpds.cli.root import app
from fpds.config import FPDS_FIELDS_CONFIG

TEXT_WRAP_WIDTH = 30


@app.command()
def fields(
    pattern: Annotated[
        Optional[str],
        typer.Option(
            "--pattern",
            "-p",
            help=(
                "String pattern to scan field name with. Will scan string and "
                "attempt to find a match at the first location. Case-insensitive."
            ),
        ),
    ] = None,
    width: Annotated[
        int, typer.Option("--width", "-w", help="Text wrap width for regex field.")
    ] = TEXT_WRAP_WIDTH,
) -> None:
    """Displays list of available FPDS fields and their descriptions.

    \b
    Usage:
        $ uv run fpds fields [OPTIONS]

    \b
    Example(s):
        $ uv run fpds fields -p vendor

    """

    data = []
    prog = re.compile(pattern, flags=re.I) if pattern else None

    def text_wrap(text: str, width: int = width) -> str:
        return textwrap.fill(text=text, width=width)

    for field in FPDS_FIELDS_CONFIG:
        if prog and not prog.search(field["name"]):
            continue

        data.append(
            [
                field["name"],
                text_wrap(field["description"], width=20),
                text_wrap(field["regex"], width=width),
            ]
        )

    print(
        tabulate(data, headers=["Name", "Description", "Regex"], tablefmt="fancy_grid")
    )
