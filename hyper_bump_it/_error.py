"""
Errors raised by the library.
"""
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Collection, TypeVar

from pydantic import ValidationError

if TYPE_CHECKING:
    from pydantic.error_wrappers import ErrorDict

from hyper_bump_it._text_formatter import keys


class BumpItError(Exception):
    """Base for library errors"""

    def __rich__(self) -> str:
        return str(self)


class FormatError(BumpItError):
    """Base for formatting errors"""


class FormatKeyError(FormatError):
    """Pattern referenced an invalid key"""

    def __init__(self, format_pattern: str, valid_keys: Collection[str]) -> None:
        self.format_pattern = format_pattern
        self.valid_keys = FormatKeyError._sort_keys(valid_keys)
        super().__init__(
            f"Format pattern '{self.format_pattern}' used an invalid key. "
            f"Valid keys are: {_list_str_values(self.valid_keys)}"
        )

    def __rich__(self) -> str:
        return (
            f"Format pattern '{_rich_invalid_value(self.format_pattern)}' used an invalid key.\n"
            f"Valid keys are: {_list_values(self.valid_keys, _rich_valid_value)}"
        )

    @staticmethod
    def _sort_keys(valid_keys: Collection[str]) -> tuple[str, ...]:
        """
        Re-order keys for display to the user.

        The ordering first sorts by general keys, current keys, new keys.
        Within each of those sections, the order is based on the order of the version parts. Any
        helper keys go after the version part keys.
        """
        preferred_order = {
            keys.VERSION: 0,
            keys.MAJOR: 1,
            keys.MINOR: 2,
            keys.PATCH: 3,
            keys.PRERELEASE: 4,
            keys.BUILD: 5,
            keys.TODAY: 6,
        }

        def _key_order(value: str) -> tuple[int, str, int]:
            parts = value.split("_")
            part_count = len(parts)
            if part_count == 1:
                return part_count, "", preferred_order[parts[0]]
            return len(parts), parts[0], preferred_order[parts[1]]

        return tuple(sorted(valid_keys, key=_key_order))


class FormatPatternError(FormatError):
    """Pattern was not properly formed"""

    def __init__(self, format_pattern: str, error: str) -> None:
        self.format_pattern = format_pattern
        self.error = error
        super().__init__(
            f"Format pattern '{self.format_pattern}' was invalid: {self.error}"
        )

    def __rich__(self) -> str:
        return (
            f"Format pattern '{_rich_invalid_value(self.format_pattern)}' was invalid:\n"
            f"{_rich_error_message(self.error)}"
        )


class TodayFormatKeyError(FormatError):
    """Today key using unsupported format directive"""

    def __init__(self, date_format_pattern: str, valid_keys: Collection[str]) -> None:
        self.date_format_pattern = date_format_pattern
        self.valid_keys = valid_keys
        super().__init__(
            f"Today format directive '{self.date_format_pattern}' used an unsupported key for "
            f"keystone parsing. Valid keys are: {_list_str_values(self.valid_keys)}"
        )

    def __rich__(self) -> str:
        return (
            f"Today format directive '{_rich_invalid_value(self.date_format_pattern)}' "
            "used an unsupported key for keystone parsing.\n"
            f"Valid keys are: {_list_values(self.valid_keys, _rich_valid_value)}"
        )


class IncompleteKeystoneVersionError(FormatError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"Keystone version found in file '{self.file}' using pattern '{self.search_pattern}'"
            f" was incomplete."
        )

    def __rich__(self) -> str:
        return (
            f"Keystone version found in file '{_rich_path(self.file)}' using pattern "
            f"'{_rich_invalid_value(self.search_pattern)}' was incomplete."
        )


class FileGlobError(BumpItError):
    def __init__(self, working_dir: Path, file_glob: str) -> None:
        self.working_dir = working_dir
        self.file_glob = file_glob
        super().__init__(
            f"File glob '{self.file_glob}' did not match any files in '{self.working_dir}'"
        )

    def __rich__(self) -> str:
        return (
            f"File glob '{_rich_file_glob(self.file_glob)}' did not match any files "
            f"in '{_rich_path(self.working_dir)}'"
        )


class KeystoneError(BumpItError):
    """Base for keystone file errors"""


class KeystoneFileGlobError(KeystoneError):
    _NO_MATCH_TEXT = "No files matched"

    def __init__(self, file_glob: str, matches: list[Path]) -> None:
        self.file_glob = file_glob
        self.matches = matches
        super().__init__(
            f"The file glob ({self.file_glob}) for the keystone files must match exactly one "
            f"file. {self._matched_description(str)}"
        )

    def __rich__(self) -> str:
        return (
            f"The file glob ({_rich_file_glob(self.file_glob)}) for the keystone files must match "
            f"exactly one file.\n{self._matched_description(_rich_path)}"
        )

    def _matched_description(self, to_str: Callable[[Path], str]) -> str:
        if self.matches:
            return f"Matched: {_list_values(self.matches, to_str)}"
        return KeystoneFileGlobError._NO_MATCH_TEXT


class VersionNotFound(KeystoneError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"Current version not found in file '{self.file}' using pattern "
            f"'{self.search_pattern}'"
        )

    def __rich__(self) -> str:
        return (
            f"Current version not found in file '{_rich_path(self.file)}' using pattern "
            f"'{_rich_valid_value(self.search_pattern)}'"
        )


class GitError(BumpItError):
    """Base for git errors"""


class NoRepositoryError(GitError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(
            f"The project root '{self.project_root}' is not a git repository"
        )

    def __rich__(self) -> str:
        return f"The project root '{_rich_path(self.project_root)}' is not a git repository"


class EmptyRepositoryError(GitError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(f"The repository at '{self.project_root}' has no commits")

    def __rich__(self) -> str:
        return f"The repository at '{_rich_path(self.project_root)}' has no commits"


class DirtyRepositoryError(GitError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(
            f"The repository at '{self.project_root}' has uncommitted changes"
        )

    def __rich__(self) -> str:
        return f"The repository at '{_rich_path(self.project_root)}' has uncommitted changes"


class DetachedRepositoryError(GitError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(
            f"The repository at '{self.project_root}' is not currently on a branch"
        )

    def __rich__(self) -> str:
        return f"The repository at '{_rich_path(self.project_root)}' is not currently on a branch"


class MissingRemoteError(GitError):
    def __init__(self, remote: str, project_root: Path) -> None:
        self.project_root = project_root
        self.remote = remote
        super().__init__(
            f"The repository at '{self.project_root}' does not define the remote '{self.remote}'"
        )

    def __rich__(self) -> str:
        return (
            f"The repository at '{_rich_path(self.project_root)}' does not define the "
            f"[bold]remote[/] '{_rich_valid_value(self.remote)}'"
        )


class AlreadyExistsError(GitError):
    def __init__(self, ref_type: str, name: str, project_root: Path) -> None:
        self.project_root = project_root
        self.ref_type = ref_type
        self.name = name
        super().__init__(
            f"The repository at '{self.project_root}' already has a {self.ref_type} named "
            f"'{self.name}'"
        )

    def __rich__(self) -> str:
        return (
            f"The repository at '{_rich_path(self.project_root)}' already has a "
            f"{_rich_bold(self.ref_type)} named '{_rich_valid_value(self.name)}'"
        )


class ConfigurationError(BumpItError):
    """Base for configuration errors"""


class ConfigurationFileNotFoundError(ConfigurationError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(
            f"No configuration file found in directory {self.project_root.resolve()}"
        )

    def __rich__(self) -> str:
        return (
            f"No configuration file found in directory "
            f"{_rich_path(self.project_root.resolve())}"
        )


class ConfigurationFileReadError(ConfigurationError):
    def __init__(self, file: Path, cause: Exception) -> None:
        self.file = file
        self.cause = cause
        super().__init__(
            f"The configuration file ({self.file}) could not be read: {self.cause}"
        )

    def __rich__(self) -> str:
        return (
            f"The configuration file ({_rich_path(self.file)}) could not be read:\n"
            + _rich_error_message(str(self.cause))
        )


class ConfigurationFileWriteError(ConfigurationError):
    def __init__(self, file: Path, cause: Exception) -> None:
        self.file = file
        self.cause = cause
        super().__init__(
            f"The configuration file ({self.file}) could not be written to: {self.cause}"
        )

    def __rich__(self) -> str:
        return (
            f"The configuration file ({_rich_path(self.file)}) could not be written to:\n"
            + _rich_error_message(str(self.cause))
        )


class SubTableNotExistError(ConfigurationError):
    def __init__(self, file: Path, sub_tables: tuple[str, str]) -> None:
        self.file = file
        self.sub_table = ".".join(sub_tables)
        super().__init__(
            f"The configuration file ({self.file}) "
            f"is missing the sub-table '{self.sub_table}'"
        )

    def __rich__(self) -> str:
        return (
            f"The configuration file ({_rich_path(self.file)}) is missing the sub-table "
            f"'{_rich_valid_value(self.sub_table)}'"
        )


class InvalidConfigurationError(ConfigurationError):
    def __init__(self, file: Path, cause: ValidationError) -> None:
        self.file = file
        self.cause = cause
        super().__init__(
            f"The configuration file ({self.file}) is not valid: {self.cause}"
        )

    # Slightly customized variant of pydantic's __str__() to make it more end user-friendly
    # and enhanced with rich styles.
    def __rich__(self) -> str:
        errors = self.cause.errors()
        no_errors = len(errors)

        return (
            f"The configuration file ({_rich_path(self.file)}) is not valid:\n"
            f'{no_errors} validation error{"" if no_errors == 1 else "s"} '
            f"for {_rich_bold(self.cause.model.__name__)}\n"
            f"{InvalidConfigurationError.display_errors(errors)}"
        )

    @staticmethod
    def display_errors(errors: list["ErrorDict"]) -> str:
        return "\n".join(
            f'{InvalidConfigurationError._display_error_loc(e)}  {_rich_error_message(e["msg"])}'
            for e in errors
        )

    @staticmethod
    def _display_error_loc(error: "ErrorDict") -> str:
        if len(error["loc"]) == 1 and error["loc"][0] == "__root__":
            return ""
        return (
            " -> ".join(f"[{_RICH_STYLE_ERROR_LOC}]{e}[/]" for e in error["loc"]) + "\n"
        )


def first_error_message(ex: ValidationError) -> str:
    return ex.errors()[0]["msg"]


# rich specific functionality
_RICH_STYLE_VALID = "green"
_RICH_STYLE_INVALID = "bold red"
_RICH_STYLE_ERROR_MESSAGE = "red"
_RICH_STYLE_ERROR_LOC = "cyan"
_RICH_STYLE_PATHLIKE = "bold bright_blue"
_RICH_STYLE_FILE_GLOB = "deep_sky_blue1"


def _rich_valid_value(value: str) -> str:
    return _rich_value(value, _RICH_STYLE_VALID)


def _rich_invalid_value(value: str) -> str:
    return _rich_value(value, _RICH_STYLE_INVALID)


def _rich_error_message(value: str) -> str:
    return _rich_value(value, _RICH_STYLE_ERROR_MESSAGE)


def _rich_path(value: Path) -> str:
    return _rich_value(str(value), _RICH_STYLE_PATHLIKE)


def _rich_file_glob(value: str) -> str:
    return _rich_value(value, _RICH_STYLE_FILE_GLOB)


def _rich_bold(value: str) -> str:
    return _rich_value(value, "bold")


def _rich_value(value: str, style: str) -> str:
    return f"[{style}]{value}[/]"


TValue = TypeVar("TValue")


def _list_str_values(values: Collection[str]) -> str:
    return ", ".join(value for value in values)


def _list_values(values: Collection[TValue], to_str: Callable[[TValue], str]) -> str:
    return ", ".join(to_str(value) for value in values)
