"""
fpds mixin classes

author: derek663@gmail.com
last_updated: 2024-06-05
"""


class fpdsMixin:
    @property
    def url_base(self) -> str:
        """Base URL for all ATOM feed requests"""
        return "https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC"
