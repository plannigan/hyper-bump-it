"""
Errors raised by the library.
"""
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Collection, Literal, TypeVar, Union

from pydantic import ValidationError
from rich.text import Text

from . import ui

if TYPE_CHECKING:
    from pydantic.error_wrappers import ErrorDict


class BumpItError(Exception):
    """Base for library errors"""

    def __rich__(self) -> Text:
        return Text(str(self))


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

    def __rich__(self) -> Text:
        message = Text("Format pattern '")
        message.append(self.format_pattern, style="invalid")
        message.append("' used an invalid key.\nValid keys are: ")
        message.append_text(ui.list_styled_values(self.valid_keys, "valid"))
        return message

    @staticmethod
    def _sort_keys(valid_keys: Collection[str]) -> tuple[str, ...]:
        """
        Re-order keys for display to the user.

        The ordering first sorts by general keys, current keys, new keys.
        Within each of those sections, the order is based on the order of the version parts. Any
        helper keys go after the version part keys.
        """
        from .format_pattern import keys  # prevents circular import

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

    def __rich__(self) -> Text:
        message = Text("Format pattern '")
        message.append(self.format_pattern, style="invalid")
        message.append("' was invalid:\n")
        message.append(self.error, style="error.msg")
        return message


class TodayFormatKeyError(FormatError):
    """Today key using unsupported format directive"""

    def __init__(self, date_format_pattern: str, valid_keys: Collection[str]) -> None:
        self.date_format_pattern = date_format_pattern
        self.valid_keys = valid_keys
        super().__init__(
            f"Today format directive '{self.date_format_pattern}' used an unsupported key for "
            f"keystone parsing. Valid keys are: {_list_str_values(self.valid_keys)}"
        )

    def __rich__(self) -> Text:
        message = Text("Today format directive '")
        message.append(self.date_format_pattern, style="invalid")
        message.append(
            "' used an unsupported key for keystone parsing.\nValid keys are: "
        )
        message.append_text(ui.list_styled_values(self.valid_keys, "valid"))
        return message


class IncompleteKeystoneVersionError(FormatError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"Keystone version found in file '{self.file}' using pattern '{self.search_pattern}'"
            f" was incomplete."
        )

    def __rich__(self) -> Text:
        message = Text("Keystone version found in file '")
        message.append(str(self.file), style="file.path")
        message.append("' using pattern '")
        message.append(str(self.search_pattern), style="invalid")
        message.append("' was incomplete.")
        return message


class FileGlobError(BumpItError):
    def __init__(self, working_dir: Path, file_glob: str) -> None:
        self.working_dir = working_dir
        self.file_glob = file_glob
        super().__init__(
            f"File glob '{self.file_glob}' did not match any files in '{self.working_dir}'."
        )

    def __rich__(self) -> Text:
        message = Text("File glob '")
        message.append(self.file_glob, style="file.glob")
        message.append("' did not match any files in '")
        message.append(str(self.working_dir), style="file.path")
        message.append("'.")
        return message


class KeystoneError(BumpItError):
    """Base for keystone file errors"""


class KeystoneFileGlobError(KeystoneError):
    _NO_MATCH_TEXT = "No files matched"

    def __init__(self, file_glob: str, matches: list[Path]) -> None:
        self.file_glob = file_glob
        self.matches = matches
        message = (
            f"The file glob ({self.file_glob}) "
            "for the keystone files must match exactly one file."
        )
        if self.matches:
            message = f"{message} Matched: {_list_values(self.matches, str)}"
        else:
            message = f"{message} {KeystoneFileGlobError._NO_MATCH_TEXT}"
        super().__init__(message)

    def __rich__(self) -> Text:
        message = Text("The file glob (")
        message.append(self.file_glob, style="file.glob")
        message.append(") for the keystone files must match exactly one file.\n")
        if self.matches:
            message.append("Matched: ")
            message.append_text(
                ui.list_styled_values(
                    [str(match) for match in self.matches], style="file.path"
                )
            )
        else:
            message.append(KeystoneFileGlobError._NO_MATCH_TEXT)
        return message


class SearchTextNotFound(KeystoneError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"The search pattern '{self.search_pattern}' was not found in file '{self.file}'"
        )

    def __rich__(self) -> Text:
        message = Text("The search pattern '")
        message.append(self.search_pattern, style="format.pattern")
        message.append("' was not found in file '")
        message.append(str(self.file), style="file.path")
        message.append("'")
        return message


class VersionNotFound(KeystoneError):
    def __init__(self, file: Path, search_pattern: str) -> None:
        self.file = file
        self.search_pattern = search_pattern
        super().__init__(
            f"Current version not found in file '{self.file}' using pattern "
            f"'{self.search_pattern}'"
        )

    def __rich__(self) -> Text:
        message = Text("Current version not found in file '")
        message.append(str(self.file), style="file.path")
        message.append("' using pattern '")
        message.append(self.search_pattern, style="valid")
        message.append("'")
        return message


class GitError(BumpItError):
    """Base for git errors"""

    def __init__(self, project_root: Path, message_suffix: str) -> None:
        self.project_root = project_root
        super().__init__(f"The project root '{self.project_root}' {message_suffix}")

    @property
    def _message_prefix(self) -> Text:
        return (
            Text("The project root '")
            .append(str(self.project_root), style="file.path")
            .append("' ")
        )


class GitErrorSimple(GitError):
    """Base for git errors that don't need styling of the suffix"""

    def __init__(self, project_root: Path, message_suffix: str) -> None:
        self.message_suffix = message_suffix
        super().__init__(project_root, self.message_suffix)

    def __rich__(self) -> Text:
        return self._message_prefix.append(self.message_suffix)


class NoRepositoryError(GitErrorSimple):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root, "is not a git repository")


class EmptyRepositoryError(GitErrorSimple):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root, "has no commits")


class DirtyRepositoryError(GitErrorSimple):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root, "has uncommitted changes")


class DetachedRepositoryError(GitErrorSimple):
    def __init__(self, project_root: Path) -> None:
        super().__init__(project_root, "is not currently on a branch")


class MissingRemoteError(GitError):
    def __init__(self, remote: str, project_root: Path) -> None:
        self.remote = remote
        super().__init__(project_root, f"does not define the remote '{self.remote}'")

    def __rich__(self) -> Text:
        return (
            self._message_prefix.append("does not define the ")
            .append("remote", style="emphasis")
            .append(" '")
            .append(self.remote, style="vcs.remote")
            .append("'")
        )


class DisallowedInitialBranchError(GitError):
    def __init__(
        self,
        allowed_initial_branches: frozenset[str],
        active_branch: str,
        project_root: Path,
    ) -> None:
        self.allowed_initial_branches = allowed_initial_branches
        self.active_branch = active_branch
        if len(self.allowed_initial_branches) == 1:
            must_message = f"'{self._first_branch}'"
        else:
            branches = "', '".join(self.allowed_initial_branches)
            must_message = f"one of: '{branches}'"
        super().__init__(
            project_root,
            f"is currently on branch '{self.active_branch}', "
            f"which is not allowed. Must be {must_message}.",
        )

    @property
    def _first_branch(self) -> str:
        return next(iter(self.allowed_initial_branches))

    def __rich__(self) -> Text:
        message = self._message_prefix.append("is currently on branch '")
        message.append(self.active_branch, style="vcs.branch")
        message.append("', which is not allowed. Must be ")
        if len(self.allowed_initial_branches) == 1:
            message.append("'")
            message.append(self._first_branch, style="vcs.branch")
            message.append("'")
        else:
            message.append("one of: ")
            message.append_text(
                ui.list_styled_values(
                    self.allowed_initial_branches, style="vcs.branch", quoted=True
                )
            )
        message.append(".")
        return message


class AlreadyExistsError(GitError):
    def __init__(
        self,
        ref_type: Union[Literal["branch"], Literal["tag"]],
        name: str,
        project_root: Path,
    ) -> None:
        self.project_root = project_root
        self.ref_type = ref_type
        self.name = name
        super().__init__(
            project_root, f"already has a {self.ref_type} named '{self.name}'"
        )

    def __rich__(self) -> Text:
        return (
            self._message_prefix.append("already has a ")
            .append(self.ref_type, style="emphasis")
            .append(" named '")
            .append(self.name, style=f"vcs.{self.ref_type}")
            .append("'")
        )


class ConfigurationError(BumpItError):
    """Base for configuration errors"""


class ConfigurationFileNotFoundError(ConfigurationError):
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        super().__init__(
            f"No configuration file found in directory {self.project_root}"
        )

    def __rich__(self) -> Text:
        return Text("No configuration file found in directory ").append(
            str(self.project_root), style="file.path"
        )


class ConfigurationFileError(ConfigurationError):
    def __init__(self, file: Path, message_suffix: str) -> None:
        self.file = file
        super().__init__(f"The configuration file ({self.file}) {message_suffix}")

    @property
    def _message_prefix(self) -> Text:
        return (
            Text("The configuration file (")
            .append(str(self.file), style="file.path")
            .append(") ")
        )


class ConfigurationFileReadError(ConfigurationFileError):
    def __init__(self, file: Path, cause: Exception) -> None:
        self.cause = cause
        super().__init__(file, f"could not be read: {self.cause}")

    def __rich__(self) -> Text:
        return self._message_prefix.append("could not be read:\n").append(
            str(self.cause), style="error.msg"
        )


class SubTableNotExistError(ConfigurationFileError):
    def __init__(self, file: Path, sub_tables: tuple[str, str]) -> None:
        self.sub_table = ".".join(sub_tables)
        super().__init__(file, f"is missing the sub-table '{self.sub_table}'")

    def __rich__(self) -> Text:
        return (
            self._message_prefix.append("is missing the sub-table '")
            .append(str(self.sub_table), style="valid")
            .append("'")
        )


class InvalidConfigurationError(ConfigurationFileError):
    def __init__(self, file: Path, cause: ValidationError) -> None:
        self.cause = cause
        super().__init__(file, f"is not valid: {self.cause}")

    # Slightly customized variant of pydantic's __str__() to make it more end user-friendly
    # and enhanced with rich styles.
    def __rich__(self) -> Text:
        errors = self.cause.errors()
        num_errors = len(errors)

        message = self._message_prefix.append("is not valid:\n")
        message.append(f"{num_errors} validation error")
        if num_errors != 1:
            message.append("s")
        message.append(" for ")
        message.append(self.cause.model.__name__, style="emphasis")
        message.append("\n")
        message.append(InvalidConfigurationError.display_errors(errors))
        return message

    @staticmethod
    def display_errors(errors: list["ErrorDict"]) -> Text:
        return Text("\n").join(
            InvalidConfigurationError._display_error_loc(e)
            .append("  ")
            .append(e["msg"], style="error.msg")
            for e in errors
        )

    @staticmethod
    def _display_error_loc(error: "ErrorDict") -> Text:
        if len(error["loc"]) == 1 and error["loc"][0] == "__root__":
            return Text("")
        return (
            Text(" -> ")
            .join(Text(str(e), style="error.loc") for e in error["loc"])
            .append("\n")
        )


def first_error_message(ex: ValidationError) -> str:
    return ex.errors()[0]["msg"]


TValue = TypeVar("TValue")


def _list_str_values(values: Collection[str]) -> str:
    return ", ".join(value for value in values)


def _list_values(values: Collection[TValue], to_str: Callable[[TValue], str]) -> str:
    return ", ".join(to_str(value) for value in values)
