"""
Errors raised by the library.
"""
from pathlib import Path
from typing import Collection

from git import Repo


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
