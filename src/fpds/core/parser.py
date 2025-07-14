"""
Core class for converting FPDS XML
tree into JSON.

author: derek663@gmail.com
last_updated: 2025-07-14
"""

import asyncio
import multiprocessing
import warnings
from asyncio import Semaphore
from concurrent.futures import ProcessPoolExecutor
from typing import AsyncGenerator, List, Optional
from urllib import parse
from urllib.request import urlopen

from aiohttp import ClientSession
from tqdm import tqdm

from fpds.core import FPDS_ENTRY
from fpds.core.mixins import fpdsMixin
from fpds.core.xml import fpdsSubTree, fpdsTree
from fpds.errors import fpdsMaxPageLengthExceededError, fpdsMissingKeywordParameterError
from fpds.utilities import validate_kwarg


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
        page: Optional[int] = None,
        **kwargs: str,
    ) -> None:
        self.cli_run = cli_run
        self.skip_regex_validation = skip_regex_validation
        self.thread_count = thread_count
        self.page = page
        self.links = []  # type: List[str]

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

    async def convert(self, session: ClientSession, link: str) -> fpdsSubTree:
        """Retrieves content from FPDS ATOM feed as a SubTree instance."""
        async with session.get(link) as response:
            content = await response.read()
            subtree = fpdsSubTree(content=content)
            return subtree

    async def fetch(self) -> List[fpdsSubTree]:
        """Asynchronously parses all ATOM feed pages for current request."""
        semaphore = Semaphore(self.thread_count)

        if not self.links:
            return []

        async with semaphore:
            async with ClientSession() as session:
                tasks = [self.convert(session, link) for link in self.links]
                return await asyncio.gather(*tasks)

    def page_index(self) -> Optional[int]:
        """Converts `page` to index integer."""
        idx = None
        if self.page:
            idx = 0 if self.page == 1 else self.page - 1
        return idx

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
        num_processes = multiprocessing.cpu_count()
        data = await self.fetch()  # List[fpdsSubTree]

        with ProcessPoolExecutor(max_workers=num_processes) as pool:
            with tqdm(total=len(data)) as progress:
                futures = []

                # allows tqdm progress bar to display correctly
                for record in data:
                    future = pool.submit(self._jsonify, record)
                    future.add_done_callback(lambda p: progress.update())
                    futures.append(future)

                for future in futures:
                    result = future.result()
                    for entry in result:
                        yield entry

    async def data(self) -> List[FPDS_ENTRY]:
        """Collects all FPDS records into a list.

        Returns
        -------
        records: `List[FPDS_ENTRY]`
            FPDS records as a list of dictionaries with de-nested XML attributes.
        """
        records = []
        async for entry in self.iter_data():
            records.append(entry)
        return records
