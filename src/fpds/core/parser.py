"""
Base classes for FPDS XML elements

author: derek663@gmail.com
last_updated: 12/03/2023
"""
import asyncio
import time
from typing import Any, List, Optional, Union
from xml.etree.ElementTree import ElementTree, fromstring

import aiohttp
import requests

from fpds.config import FPDS_FIELDS_CONFIG as FIELDS
from fpds.core import FPDS_ENTRY
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

    Parameters
    ----------
    cli_run: `bool`
        Flag indicating if this class is being isntantiated by a CLI run.
        Defaults to `False`.
    target_database_url_env_key: `str`
        Database URL environment key to insert data into.

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
        target_database_url_env_key: Union[str, None] = None,
        **kwargs,
    ):
        self.cli_run = cli_run
        self.content = []  # type: List[ElementTree]
        # TEST
        self.links = []
        self.target_database_url_env_key = target_database_url_env_key
        if kwargs:
            self.kwargs = kwargs
        else:
            raise ValueError("You must provide at least one keyword parameter")

        # do not run class validations since CLI command has its own
        if not self.cli_run:
            for kwarg, value in self.kwargs.items():
                self.kwargs[kwarg] = validate_kwarg(kwarg=kwarg, string=value)

    def __str__(self) -> str:
        """String representation of `fpdsRequest`"""
        kwargs_str = " ".join([f"{key}={value}" for key, value in self.kwargs.items()])
        return f"<fpdsRequest {kwargs_str}>"

    def __call__(self) -> Union[None, List[FPDS_ENTRY]]:
        """Shortcut for making an API call and retrieving content"""
        data = self.parse_content()

        if self.target_database_url_env_key:
            from fpds.utilities.db import insert

            insert(
                data=data,
                request_url=self.__url__(),
                target_database_url_env_key=self.target_database_url_env_key,
            )
            return None
        else:
            return data

    def __url__(self) -> str:
        """Custom magic method for request URL"""
        return f"{self.url_base}&q={self.search_params}"

    @property
    def search_params(self) -> str:
        """Search parameters inputted by user"""
        _params = [f"{key}:{value}" for key, value in self.kwargs.items()]
        return " ".join(_params)

    @staticmethod
    def convert_to_lxml_tree(content: str) -> ElementTree:
        """Returns lxml tree element from a bytes response"""
        tree = ElementTree(fromstring(content))
        return tree

    def send_request(self, url: Optional[str] = None) -> None:
        """Sends request to FPDS Atom feed

        Parameters
        ----------
        url: `str`, optional
            A URL to send a GET request to. If not provided, this method
            will default to using `url_base`
        """
        response = requests.get(
            url=self.url_base if not url else url, params={"q": self.search_params}
        )
        response.raise_for_status()
        content_tree = self.convert_to_lxml_tree(response.content.decode("utf-8"))
        self.content.append(content_tree)

    async def fetch(self, session, link) -> None:
        async with session.get(link) as response:
            content = await response.read()
            xml = fpdsXML(content=self.convert_to_lxml_tree(content))
            return xml

    async def fetch_all(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, link) for link in self.links]
            return await asyncio.gather(*tasks)

    async def compile_response(self):
        start_time = time.time()
        content = await self.fetch_all()
        end_time = time.time()
        print(f"Elapsed time: {end_time - start_time} seconds")
        return content

    def run(self):
        loop = asyncio.get_event_loop()
        records = loop.run_until_complete(self.compile_response())
        return records

    def create_content_iterable(self) -> None:
        """Paginates through a response and creates an iterable of XML trees.
        This method will not have a return but rather, will set the `content`
        attribute to an iterable of XML ElementTrees'
        """
        self.send_request()
        params = self.search_params
        tree = fpdsXML(content=self.content[0])

        links = tree.pagination_links(params=params)
        if len(links) > 1:
            links.pop(0)
        self.links = links

    def parse_content(self) -> List[FPDS_ENTRY]:
        """Parses a content iterable and generates a list of records"""
        self.create_content_iterable()
        records = []
        for tree in self.content:
            xml = fpdsXML(content=tree)
            records.extend(xml.jsonified_entries())
        return records
