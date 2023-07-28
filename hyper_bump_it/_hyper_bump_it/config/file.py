from collections.abc import Sequence
from pathlib import Path
from typing import Annotated, Optional, Union, cast

import tomlkit
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    WrapValidator,
    model_validator,
)
from pydantic_core.core_schema import ValidatorFunctionWrapHandler
from tomlkit import TOMLDocument
from tomlkit.exceptions import TOMLKitError

from ..compat import TypeAlias
from ..error import (
    ConfigurationFileNotFoundError,
    ConfigurationFileReadError,
    InvalidConfigurationError,
    SubTableNotExistError,
)
from ..planned_changes import PlannedChange
from ..version import Version
from .core import (
    DEFAULT_ALLOWED_INITIAL_BRANCHES,
    DEFAULT_BRANCH_ACTION,
    DEFAULT_BRANCH_FORMAT_PATTERN,
    DEFAULT_COMMIT_ACTION,
    DEFAULT_COMMIT_FORMAT_PATTERN,
    DEFAULT_REMOTE,
    DEFAULT_SEARCH_PATTERN,
    DEFAULT_TAG_ACTION,
    DEFAULT_TAG_MESSAGE_FORMAT_PATTERN,
    DEFAULT_TAG_NAME_FORMAT_PATTERN,
    HYPER_CONFIG_FILE_NAME,
    PYPROJECT_FILE_NAME,
    GitAction,
    validate_git_action_combination,
)

ROOT_TABLE_KEY = "hyper-bump-it"
PYPROJECT_SUB_TABLE_KEYS = ("tool", ROOT_TABLE_KEY)


class HyperBaseMode(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_min_length=1, frozen=True, strict=True
    )


def _check_action(
    value: Optional[object], handler: ValidatorFunctionWrapHandler
) -> GitAction:
    if isinstance(value, str):
        for action in GitAction:
            if value == action.value:
                return action
        raise ValueError(f"value must be one of: {', '.join(GitAction)}")
    return cast(GitAction, handler(value))


PossiblyStrGitAction = Annotated[GitAction, WrapValidator(_check_action)]


class GitActions(HyperBaseMode):
    commit: PossiblyStrGitAction = DEFAULT_COMMIT_ACTION
    branch: PossiblyStrGitAction = DEFAULT_BRANCH_ACTION
    tag: PossiblyStrGitAction = DEFAULT_TAG_ACTION

    @model_validator(mode="after")
    def _check_git_actions(
        self,
    ) -> "GitActions":
        validate_git_action_combination(
            commit=self.commit, branch=self.branch, tag=self.tag
        )
        return self


class Git(HyperBaseMode):
    remote: str = DEFAULT_REMOTE
    commit_format_pattern: str = DEFAULT_COMMIT_FORMAT_PATTERN
    branch_format_pattern: str = DEFAULT_BRANCH_FORMAT_PATTERN
    tag_name_format_pattern: str = DEFAULT_TAG_NAME_FORMAT_PATTERN
    tag_message_format_pattern: str = DEFAULT_TAG_MESSAGE_FORMAT_PATTERN
    allowed_initial_branches: frozenset[str] = DEFAULT_ALLOWED_INITIAL_BRANCHES
    extend_allowed_initial_branches: frozenset[str] = frozenset()
    actions: GitActions = GitActions()


class File(HyperBaseMode):
    file_glob: str  # relative to project root directory
    keystone: bool = False
    search_format_pattern: str = DEFAULT_SEARCH_PATTERN
    replace_format_pattern: Optional[str] = None


HyperConfigFileValues: TypeAlias = dict[str, Union[list[File], Optional[str], Git]]


def _check_version(
    value: Optional[object], handler: ValidatorFunctionWrapHandler
) -> Optional[Version]:
    if isinstance(value, str):
        return Version.parse(value)
    return cast(Version, handler(value))


OptionalVersion = Annotated[Optional[Version], WrapValidator(_check_version)]


class ConfigFile(HyperBaseMode):
    files: list[File] = Field(..., min_length=1)
    current_version: OptionalVersion = None
    show_confirm_prompt: bool = True
    git: Git = Git()

    @model_validator(mode="after")
    def _check_keystone_files(self) -> "ConfigFile":
        keystone_file_count = sum(1 for file in self.files if file.keystone)
        if keystone_file_count > 1:
            raise ValueError("Only one file is allowed to be a keystone file")
        if self.current_version is None:
            if keystone_file_count == 0:
                raise ValueError(
                    "current_version must be set if there is not a keystone file"
                )
        elif keystone_file_count != 0:
            raise ValueError(
                "Configuration can't specify the current_version while also having a keystone file"
            )
        return self

    @property
    def keystone_config(self) -> Optional[tuple[str, str]]:
        for file in self.files:
            if file.keystone:
                return file.file_glob, file.search_format_pattern
        return None


class ConfigVersionUpdater:
    def __init__(
        self,
        config_file: Path,
        project_root: Path,
        full_document: TOMLDocument,
        config_table: TOMLDocument,
        newline: Optional[str],
    ) -> None:
        """
        Initialize instance.

        :param config_file: File to write updated contents to.
        :param project_root: Directory to look for a configuration file.
        :param full_document: Config document to be written to file. Possibly including other
            values beyond what is used for this program.
        :param config_table: Config document with only the values used for this program.
        :param newline: New line character sequence for the file. `None` if no new line characters
            are found.
        """
        self._config_file = config_file
        self._project_root = project_root
        self._full_document = full_document
        self._config_table = config_table
        self._newline = newline

    def __call__(self, new_version: Version) -> PlannedChange:
        """
        Write the new version back to the configuration file.

        :param new_version: Version that should be stored in the configuration file.
        :return: Representation of the update to occur to the configuration file.
        """
        old_content = self._full_document_text
        self._config_table["current_version"] = str(new_version)
        new_content = self._full_document_text
        return PlannedChange(
            self._config_file,
            self._project_root,
            old_content=old_content,
            new_content=new_content,
            newline=self._newline,
        )

    @property
    def _full_document_text(self) -> str:
        return tomlkit.dumps(self._full_document)


ConfigReadResult: TypeAlias = tuple[ConfigFile, Optional[ConfigVersionUpdater]]


def read_config(config_file: Optional[Path], project_root: Path) -> ConfigReadResult:
    """
    Read the appropriate configuration file.

    If `config_file` is given, that will be used as the dedicated configuration file to read.
    If `config_file` is not given, look for a configuration file in the project root. First check
    for a dedicated configuration file. If that doesn't exist, try pyproject.toml.

    :param config_file: Hyper config file to read from.
    :param project_root: Directory to look for a configuration file.
    :return: Parsed configuration content and an object that can be used to update the version
        stored in the configuration file. If the configuration uses a keystone file, this second
        values will be `None`.
    :raises ConfigurationError: No file was found or there was some error in the file.
    """
    if config_file is not None:
        return read_hyper_config(config_file, project_root)

    hyper_config_file = project_root / HYPER_CONFIG_FILE_NAME
    if hyper_config_file.exists():
        return read_hyper_config(hyper_config_file, project_root)

    pyproject_config_file = project_root / PYPROJECT_FILE_NAME
    if pyproject_config_file.exists():
        return read_pyproject_config(pyproject_config_file, project_root)

    raise ConfigurationFileNotFoundError(project_root)


def read_pyproject_config(
    pyproject_file: Path,
    project_root: Path,
) -> ConfigReadResult:
    """
    Read configuration from pyproject file.

    :param pyproject_file: Path to the file to read.
    :param project_root: Directory to look for a configuration file.
    :return: Parsed configuration content and an object that can be used to update the version
        stored in the configuration file. If the configuration uses a keystone file, this second
        values will be `None`.
    :raises ConfigurationError: Some error exists in the configuration file.
    """
    return _read_config(pyproject_file, PYPROJECT_SUB_TABLE_KEYS, project_root)


def read_hyper_config(
    hyper_config_file: Path,
    project_root: Path,
) -> ConfigReadResult:
    """
    Read configuration from pyproject file.

    :param hyper_config_file: Path to the decided configuration file to read.
    :param project_root: Directory to look for a configuration file.
    :return: Parsed configuration content and an object that can be used to update the version
        stored in the configuration file. If the configuration uses a keystone file, this second
        values will be `None`.
    :raises ConfigurationError: Some error exists in the configuration file.
    """
    return _read_config(hyper_config_file, [ROOT_TABLE_KEY], project_root)


def _read_config(
    config_file: Path, sub_tables: Sequence[str], project_root: Path
) -> ConfigReadResult:
    try:
        file_data = config_file.read_bytes()
        full_document = tomlkit.parse(file_data.decode())
    except (OSError, TOMLKitError) as ex:
        raise ConfigurationFileReadError(config_file, ex) from ex
    config_table = full_document
    for key in sub_tables:
        config_table = cast(TOMLDocument, config_table.get(key))
        if config_table is None:
            raise SubTableNotExistError(config_file, PYPROJECT_SUB_TABLE_KEYS)

    try:
        # Unwrap TOML objects so that the rest of the application operates on native types.
        config = ConfigFile(**config_table.unwrap())
    except ValidationError as ex:
        raise InvalidConfigurationError(config_file, ex)

    if config.current_version is None:
        # uses keystone file & doesn't need to write back to pyproject file.
        return config, None
    return config, ConfigVersionUpdater(
        config_file=config_file,
        project_root=project_root,
        full_document=full_document,
        config_table=config_table,
        newline=PlannedChange.detect_line_ending(file_data),
    )
