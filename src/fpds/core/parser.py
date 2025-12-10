"""
Core class for converting FPDS XML
tree into JSON.

author: derek663@gmail.com
last_updated: 2025-07-14
"""

import asyncio
import gzip
import json
import multiprocessing
from pathlib import Path
import warnings
from asyncio import Semaphore
from concurrent.futures import ProcessPoolExecutor
from typing import AsyncGenerator, List, Optional
from urllib import parse
from urllib.request import urlopen
from uuid import uuid4

from httpx import AsyncClient
from rich.progress import TaskID
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)

from fpds.core import FPDS_ENTRY
from fpds.core.mixins import fpdsMixin
from fpds.core.xml import fpdsSubTree, fpdsTree
from fpds.errors import fpdsMaxPageLengthExceededError, fpdsMissingKeywordParameterError
from fpds.utilities import validate_kwarg

from fpds.config import FPDS_DATA_DATE_DIR


class fpdsRequest(fpdsMixin):
    """Makes a GET request to the FPDS ATOM feed.

    Takes an unlimited number of arguments. All query parameters should be
    submitted as strings. During class instantiation, this class
    will validate argument names/values and raise an Exception if any
    error exists.

    If you encounter new keyword parameters and/or an altered regex pattern,
    use :param:`skip_regex_validation` to skip regex validation. Feel free
    to submit an issue or open up a PR with new fields.

    Example:
    -------
    >>> request = fpdsRequest(
    >>>     LAST_MOD_DATE="[2022/01/01, 2022/05/01]",
    >>>     AGENCY_CODE="7504",
    >>> )

    Attributes
    ----------
    cli_run: `bool`
        Defaults to `False`.
        Flag indicating if this class is being isntantiated by a CLI run.
    skip_regex_validation: `bool`
        Defaults to `False`.
        If `True`, opts out of regex validation.
    thread_count: `int`
        Defaults to 10.
        The number of threads to send per search.
    max_chunk_size_mb: `int`
        Defaults to 100.
        The maximum size of each outputted data file (uncompressed).
    page: `Optional[int]`
        Defaults to `None`.
        The page of results to retrieve.
    **kwargs: `str`
        Any valid FPDS keyword search parameter.

    Raises
    ------
    fpdsDuplicateParameterConfiguration:
        Raised if duplicate configurations for a single parameter exist.

    fpdsInvalidParameter:
        Raised if an invalid parameter is provided.

    fpdsMaxPageLengthExceededError:
        Raised if user requests a page of results that doesn't exist.

    fpdsMismatchedParameterRegexError:
        Raised if parameter value does not match expected regex pattern.

    fpdsMissingKeywordParameterError:
        Raised if no keyword argument(s) are provided.
    """

    def __init__(
        self,
        cli_run: bool = False,
        skip_regex_validation: bool = False,
        thread_count: int = 10,
        max_chunk_size_mb: int = 100,
        page: Optional[int] = None,
        **kwargs: str,
    ) -> None:
        self.cli_run = cli_run
        self.skip_regex_validation = skip_regex_validation
        self.thread_count = thread_count
        self.max_chunk_size_mb = max_chunk_size_mb
        self.page = page
        self.links: List[str] = []

        if kwargs:
            self.kwargs = kwargs
        else:
            raise fpdsMissingKeywordParameterError

        tree = fpdsTree(content=self.initial_request())
        links = tree.pagination_links(params=self.search_params)
        self.links = links

        if self.page:
            idx = self.page_index()
            if idx is not None and self.links:
                if self.page > self.page_count:
                    raise fpdsMaxPageLengthExceededError(page_count=self.page_count)
                self.links = [links[idx]]

        # do not run class validations since CLI command has its own
        if not self.cli_run:
            if not self.skip_regex_validation:
                for kwarg, value in self.kwargs.items():
                    self.kwargs[kwarg] = validate_kwarg(kwarg=kwarg, string=value)
            else:
                warnings.warn("Opting out of regex validation!")

    def __str__(self) -> str:  # pragma: no cover
        """String representation of `fpdsRequest`."""
        kwargs_str = " ".join([f"{key}={value}" for key, value in self.kwargs.items()])
        return f"<fpdsRequest {kwargs_str}>"

    def __url__(self) -> str:  # pragma: no cover
        """Custom magic method for request URL."""
        return f"{self.url_base}&q={self.search_params}"

    @property
    def search_params(self) -> str:
        """Search parameters inputted by user."""
        _params = [f"{key}:{value}" for key, value in self.kwargs.items()]
        return " ".join(_params)

    @property
    def page_count(self) -> int:
        """Total number of FPDS pages contained in request."""
        return len(self.links)

    def initial_request(self) -> bytes:
        """Returns the root XML tree from the initial request."""
        encoded_params = parse.urlencode({"q": self.search_params})
        with urlopen(f"{self.url_base}&{encoded_params}") as response:
            content_tree = response.read()
        return content_tree

    async def convert(
        self,
        client: AsyncClient,
        link: str,
        semaphore: asyncio.Semaphore,
    ) -> fpdsSubTree:
        """Retrieves content from FPDS ATOM feed as a SubTree instance."""
        async with semaphore:
            response = await client.get(link)
            subtree = fpdsSubTree(content=response.content)
            return subtree

    async def fetch(self) -> List[fpdsSubTree]:
        """Asynchronously parses all ATOM feed pages for current request."""
        if not self.links:
            return []
        semaphore = asyncio.Semaphore(self.thread_count)

        async def convert_with_progress(
            client: AsyncClient,
            link: str,
            semaphore: asyncio.Semaphore,
            progress: Progress,
            task_id: TaskID,
        ) -> fpdsSubTree:
            result = await self.convert(client=client, link=link, semaphore=semaphore)
            progress.update(task_id=task_id, advance=1)
            return result

        with self._create_progress() as progress:
            task_id = progress.add_task("Fetching data...", total=len(self.links))
            async with AsyncClient(timeout=None) as client:
                tasks = [
                    convert_with_progress(client, link, semaphore, progress, task_id)
                    for link in self.links
                ]
                results = await asyncio.gather(*tasks)
                return results

    def page_index(self) -> Optional[int]:
        """Converts `page` to index integer."""
        idx = None
        if self.page:
            idx = 0 if self.page == 1 else self.page - 1
        return idx

    @staticmethod
    def _create_progress() -> Progress:
        """Creates a Progress instance with standard configuration."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeRemainingColumn(elapsed_when_finished=True),
        )

    @staticmethod
    def _jsonify(entry: fpdsSubTree) -> List[FPDS_ENTRY]:
        """Wrapper around `jsonify` method for avoiding pickle issue."""
        return entry.jsonify()

    async def iter_data(self) -> AsyncGenerator[FPDS_ENTRY, None]:
        """Lazily yields FPDS records as an asynchronous generator.

        Yields
        ------
        `FPDS_ENTRY`
            A single FPDS record as it becomes available.
        """
        from concurrent.futures import as_completed

        num_processes = multiprocessing.cpu_count()
        data = await self.fetch()  # List[fpdsSubTree]

        with ProcessPoolExecutor(max_workers=num_processes) as pool:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("({task.completed}/{task.total})"),
                TimeRemainingColumn(elapsed_when_finished=True),
            ) as progress:
                task_id = progress.add_task(
                    "Processing records...", total=len(data)
                )

                # Submit all tasks
                future_to_record = {
                    pool.submit(self._jsonify, record): record for record in data
                }

                # Process results as they complete and yield immediately
                for future in as_completed(future_to_record):
                    progress.update(task_id, advance=1)
                    result = future.result()
                    for entry in result:
                        yield entry


    async def data(
        self,
        output_dir: Path = FPDS_DATA_DATE_DIR,
    ) -> None:
        run_id = str(uuid4())

        # Memory-efficient chunking: write to gzip files
        output_path = (Path(output_dir) / run_id).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)

        max_bytes = self.max_chunk_size_mb * 1_048_576  # Convert MB to bytes
        file_paths: List[str] = []
        chunk_buffer: List[FPDS_ENTRY] = []
        current_size = 0
        chunk_index = 0

        async for entry in self.iter_data():
            # Convert entry to JSON string to measure size
            entry_json = json.dumps(entry)
            entry_size = len(entry_json.encode("utf-8"))

            # Check if adding this entry would exceed the chunk size
            if current_size + entry_size > max_bytes and chunk_buffer:
                # Write current buffer to gzip file
                file_path = output_path / f"{uuid4()}.json.gz"
                file_paths.append(str(file_path))

                with gzip.open(file_path, "wt", encoding="utf-8") as gz_file:
                    json.dump(chunk_buffer, gz_file)

                # Reset buffer for next chunk
                chunk_buffer = [entry]
                current_size = entry_size
                chunk_index += 1
            else:
                # Add entry to current buffer
                chunk_buffer.append(entry)
                current_size += entry_size

        # Write final chunk if there are remaining records

        if chunk_buffer:
            file_path = output_path / f"{uuid4()}.json.gz"
            file_paths.append(str(file_path))

            with gzip.open(file_path, "wt", encoding="utf-8") as gz_file:
                json.dump(chunk_buffer, gz_file)


        print(f"Wrote {len(file_paths)} chunks to {output_path}")
