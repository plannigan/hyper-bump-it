"""
Errors raised by the library.
"""
from pathlib import Path
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


class FileGlobError(BumpItError):
    def __init__(self, working_dir: Path, file_glob: str) -> None:
        self.working_dir = working_dir
        self.file_glob = file_glob
        super().__init__(
            f"File glob '{self.file_glob}' did not match any files in file '{self.working_dir}'"
        )


class VersionNotFound(BumpItError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"Current version not found in file '{self.file}' using pattern '{self.search_pattern}'"
        )
