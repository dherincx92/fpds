"""Errors for fpds."""


class fpdsMaxPageLengthExceededError(Exception):
    def __init__(self, page_count: int):
        self.message = f"Maximum response page count is {page_count}"
        super().__init__(self.message)


class fpdsMissingKeywordParameterError(Exception):
    def __init__(self):
        self.message = "You must provide at least one keyword parameter"
        super().__init__(self.message)


class fpdsMismatchedParameterRegexError(Exception):
    def __init__(self, string: str, pattern: str):
        self.message = f"`{string}` does not match regex: {pattern}"
        super().__init__(self.message)


class fpdsInvalidParameter(Exception):
    def __init__(self, name):
        self.message = f"`{name}` is not a valid FPDS parameter"
        super().__init__(self.message)


class fpdsDuplicateParameterConfiguration(Exception):
    def __init__(self, name):
        self.message = f"Multiple records for parameter `{name}` found in config!"
        super().__init__(self.message)
