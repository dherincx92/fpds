"""CLI command for retrieving FPDS federal contracts.

author: derek663@gmail.com
last_updated: 2026-01-10
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from fpds import FPDSRequest
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
        help="Positional parameters (variadic, like nargs=-1 in click)",
    ),
) -> None:
    """Sends ATOM feed request to FPDS.

    \b
    Usage:
        $ uv run fpds parse [PARAMS] [OPTIONS]

    \b
    Example(s):
        $ uv run fpds parse "LAST_MOD_DATE=[2022/01/01, 2022/03/31]"

    """

    output_dir_path: Path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    split_params = [param.split("=") for param in params]  # list[Tuple[str, str]]

    for _param in split_params:
        name, value = _param
        _param[1] = validate_kwarg(kwarg=name, string=value)

    params_kwargs = dict(split_params)
    request = FPDSRequest(cli_run=True, **params_kwargs)  # type: ignore[arg-type]
    asyncio.run(request.data(output_dir=output_dir_path))
