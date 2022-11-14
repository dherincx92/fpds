"""
Custom exceptions for validating ATOM feed search parameters

author: derek663@gmail.com
last_updated: 11/13/2022
"""

class InvalidParameter(Exception):
    """Raised if invalid parameter used with `fpds` CLI"""
    def __init__(self, param):
        self.param = param
        self.message = f"`{self.param}` is not a valid parameter"
        super().__init__(self.message)

class InvalidParameterInput(Exception):
    """Raised if input doesnt match specified regex"""
    def __init__(self, input, regex):
        self.input = input
        self.regex = regex
        self.message = f"{self.input} does not match regex: {self.regex}"
        super().__init__(self.message)