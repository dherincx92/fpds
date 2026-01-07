"""Errors for FPDS."""


class FPDSMaxPageLengthExceededError(Exception):
    def __init__(self, page_count: int) -> None:
        self.message = f"Maximum response page count is {page_count}"
        super().__init__(self.message)


class FPDSMissingKeywordParameterError(Exception):
    def __init__(self) -> None:
        self.message = "You must provide at least one keyword parameter"
        super().__init__(self.message)


class FPDSMismatchedParameterRegexError(Exception):
    def __init__(self, string: str, pattern: str) -> None:
        self.message = f"`{string}` does not match regex: {pattern}"
        super().__init__(self.message)


class FPDSInvalidParameter(Exception):
    def __init__(self, name: str) -> None:
        self.message = f"`{name}` is not a valid FPDS parameter"
        super().__init__(self.message)


class FPDSDuplicateParameterConfiguration(Exception):
    def __init__(self, name: str) -> None:
        self.message = f"Multiple records for parameter `{name}` found in config!"
        super().__init__(self.message)
