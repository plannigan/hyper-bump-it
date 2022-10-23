"""
Errors raised by the library.
"""
from typing import Collection


class BumpItError(Exception):
    """Base for library errors"""


class FormatError(BumpItError):
    """Base for formatting errors"""


class FormatKeyError(FormatError):
    """Pattern referenced an invalid key"""

    def __init__(self, format_pattern: str, valid_keys: Collection[str]) -> None:
        self.format_pattern = format_pattern
        self.valid_keys = valid_keys
        super().__init__(
            f"Format pattern '{self.format_pattern}' used an invalid key. "
            f" Valid keys are: {','.join(self.valid_keys)}"
        )


class FormatPatternError(FormatError):
    """Pattern was not properly formed"""

    def __init__(self, format_pattern: str, error: str) -> None:
        self.format_pattern = format_pattern
        self.error = error
        super().__init__(
            f"Format pattern '{self.format_pattern}' was invalid. {self.error}"
        )
