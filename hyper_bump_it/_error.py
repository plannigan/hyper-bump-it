"""
Errors raised by the library.
"""
from pathlib import Path
from typing import Collection

from git import Repo
from pydantic import ValidationError


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


class TodayFormatKeyError(FormatError):
    """Today key using unsupported format directive"""

    def __init__(self, date_format_pattern: str, valid_keys: Collection[str]) -> None:
        self.date_format_pattern = date_format_pattern
        self.valid_keys = valid_keys
        super().__init__(
            f"Today format directive '{self.date_format_pattern}' used an unsupported key for "
            f"keystone parsing. Valid keys are: {','.join(self.valid_keys)}"
        )


class IncompleteKeystoneVersionError(FormatError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"Keystone version found in file '{self.file}' using pattern '{self.search_pattern}'"
            f" was incomplete."
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


class GitError(BumpItError):
    """Base for git errors"""


class NoRepositoryError(GitError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(
            f"The project root '{self.project_root}' is not a git repository"
        )


class DirtyRepositoryError(GitError):
    def __init__(self, repository: Repo) -> None:
        self.repository = repository
        super().__init__(f"The repository '{self.repository}' has uncommitted changes")


class DetachedRepositoryError(GitError):
    def __init__(self, repository: Repo) -> None:
        self.repository = repository
        super().__init__(
            f"The repository '{self.repository}' is not currently on a branch"
        )


class MissingRemoteError(GitError):
    def __init__(self, remote: str) -> None:
        self.remote = remote
        super().__init__(f"The repository does not define the remote '{self.remote}'")


class AlreadyExistsError(GitError):
    def __init__(self, ref_type: str, name: str) -> None:
        self.ref_type = ref_type
        self.name = name
        super().__init__(
            f"The repository already has a {self.ref_type} named '{self.name}'"
        )


class ConfigurationError(BumpItError):
    """Base for configuration errors"""


class ConfigurationFileReadError(ConfigurationError):
    def __init__(self, file: Path, cause: Exception) -> None:
        self.file = file
        self.cause = cause
        super().__init__(
            f"The configuration file ({self.file}) could not be read: {self.cause}"
        )


class ConfigurationFileWriteError(ConfigurationError):
    def __init__(self, file: Path, cause: Exception) -> None:
        self.file = file
        self.cause = cause
        super().__init__(
            f"The configuration file ({self.file}) could not be written to: {self.cause}"
        )


class SubTableNotExistError(ConfigurationError):
    def __init__(self, file: Path, sub_tables: tuple[str, str]) -> None:
        self.file = file
        self.sub_tables = sub_tables
        super().__init__(
            f"The configuration file ({self.file}) "
            f"is missing the sub-table '{'.'.join(self.sub_tables)}'"
        )


class InvalidConfigurationError(ConfigurationError):
    def __init__(self, file: Path, cause: ValidationError) -> None:
        self.file = file
        self.cause = cause
        super().__init__(
            f"The configuration file ({self.file}) is not valid: {self.cause}"
        )
