"""
Base classes for FPDS XML elements.

author: derek663@gmail.com
last_updated: 07/13/2024
"""

import asyncio
import multiprocessing
from asyncio import Semaphore
from concurrent.futures import ProcessPoolExecutor
from itertools import chain
from typing import Dict, List, Optional, Union
from urllib import parse
from urllib.request import urlopen
from xml.etree.ElementTree import ElementTree, fromstring

from aiohttp import ClientSession

from fpds.core.mixins import fpdsMixin
from fpds.core.xml import fpdsXML
from fpds.utilities import validate_kwarg


class fpdsRequest(fpdsMixin):
    """Makes a GET request to the FPDS ATOM feed. Takes an unlimited number of
    arguments. All query parameters should be submitted as strings. If new
    arguments are added to the feed, add the argument to the
    `fpds/core/constants.json` file. During class instantiation, this class
    will validate argument names and values and raise a `ValueError` if any
    error exists.

    Example:
        request = fpdsRequest(
            LAST_MOD_DATE="[2022/01/01, 2022/05/01]",
            AGENCY_CODE="7504"
        )

    Attributes
    ----------
    cli_run: `bool`
        Flag indicating if this class is being isntantiated by a CLI run.
        Defaults to `False`.
    thread_count: `int`
        The number of threads to send per search.
        Default to 10.

    Raises
    ------
    ValueError:
        Raised if no keyword argument(s) are provided, a keyword argument
        is not a valid FPDS parameter, or the value of a keyword argument
        does not match the expected regex.
    """

    def __init__(
        self,
        cli_run: bool = False,
        thread_count: int = 10,
        page: Optional[int] = None,
        **kwargs,
    ):
        self.cli_run = cli_run
        self.thread_count = thread_count
        self.page = page
        self.links = []  # type: List[str]
        if kwargs:
            self.kwargs = kwargs
        else:
            raise ValueError("You must provide at least one keyword parameter")

        # do not run class validations since CLI command has its own
        if not self.cli_run:
            for kwarg, value in self.kwargs.items():
                self.kwargs[kwarg] = validate_kwarg(kwarg=kwarg, string=value)

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

    @staticmethod
    def convert_to_lxml_tree(content: Union[str, bytes]) -> ElementTree:
        """Returns lxml tree element from a `bytes` response."""
        tree = ElementTree(fromstring(content))
        return tree

    def initial_request(self) -> ElementTree:
        """Send initial request to FPDS Atom feed and returns first page."""
        encoded_params = parse.urlencode({"q": self.search_params})
        with urlopen(f"{self.url_base}&{encoded_params}") as response:
            body = response.read()

        content_tree = self.convert_to_lxml_tree(body.decode("utf-8"))
        return content_tree

    async def convert(self, session: ClientSession, link: str) -> fpdsXML:
        """Retrieves content from FPDS ATOM feed."""
        async with session.get(link) as response:
            content = await response.read()
            xml = fpdsXML(content=self.convert_to_lxml_tree(content))
            return xml

    async def fetch(self) -> List[fpdsXML]:
        self.create_request_links()
        semaphore = Semaphore(self.thread_count)

        async with semaphore:
            async with ClientSession() as session:
                tasks = [self.convert(session, link) for link in self.links]
                return await asyncio.gather(*tasks)

    def page_index(self) -> int:
        """Converts `page` to index integer."""
        idx = 0 if self.page == 1 else self.page - 1
        return idx

    def create_request_links(self) -> None:
        """Paginates through the first page of an FPDS response and creates a
        list of all pagination links. This method will not have a return; it
        will set the `links` attributes to an iterable of strings.
        """
        first_page = self.initial_request()
        params = self.search_params
        tree = fpdsXML(content=first_page)

        links = tree.pagination_links(params=params)
        self.links = links

        if self.page:
            if self.page > self.page_count:
                raise ValueError(f"Max response page count is {self.page_count}!")
            self.links = [links[self.page_index()]]

    @staticmethod
    def _jsonify(entry) -> Dict[str, str]:
        """Wrapper around `jsonify` method for avoiding pickle issue."""
        return entry.jsonify()

    async def data(self) -> List[Dict[str, Union[str, float]]]:
        num_processes = multiprocessing.cpu_count()
        data = await self.fetch()

        # for parallel processing
        with ProcessPoolExecutor(max_workers=num_processes) as pool:
            results = pool.map(self._jsonify, data)

        data = list(chain.from_iterable(results))
        return data
