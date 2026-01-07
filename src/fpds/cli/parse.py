"""
CLI command for retrieving FPDS federal contracts.

author: derek663@gmail.com
last_updated: 2026-01-06
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from fpds import fpdsRequest
from fpds.cli.root import app
from fpds.config import FPDS_DATA_DATE_DIR
from fpds.utilities import validate_kwarg


@app.command()
def parse(
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            "-o",
            file_okay=False,
            dir_okay=True,
            writable=True,
            help="Directory to output extracted FPDS data to.",
        ),
    ] = FPDS_DATA_DATE_DIR,
    params: list[str] = typer.Argument(
        ...,
        help="Positional parameters (variadic, like nargs=-1)",
    ),
) -> None:
    """Sends ATOM feed request to FPDS."""

    if output_dir:
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            dir = Path(output_dir)

    split_params = [param.split("=") for param in params]  # List[Tuple[str, str]]

    for _param in split_params:
        name, value = _param
        _param[1] = validate_kwarg(kwarg=name, string=value)

    params_kwargs = dict(split_params)
    request = fpdsRequest(cli_run=True, **params_kwargs)  # type: ignore[arg-type]
    asyncio.run(request.data(output_dir=dir))
