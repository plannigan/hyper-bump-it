from collections.abc import Sequence
from enum import Enum
from pathlib import Path
from typing import Optional, TypeAlias, Union, cast

import tomlkit
from pydantic import (
    BaseModel,
    Field,
    StrictBool,
    StrictStr,
    ValidationError,
    root_validator,
)
from semantic_version import Version
from tomlkit import TOMLDocument
from tomlkit.exceptions import TOMLKitError

from hyper_bump_it._error import (
    ConfigurationFileNotFoundError,
    ConfigurationFileReadError,
    ConfigurationFileWriteError,
    InvalidConfigurationError,
    SubTableNotExistError,
)
from hyper_bump_it._text_formatter import keys

ROOT_TABLE_KEY = "hyper-bump-it"
PYPROJECT_SUB_TABLE_KEYS = ("tool", ROOT_TABLE_KEY)
HYPER_CONFIG_FILE_NAME = "hyper-bump-it.toml"
PYPROJECT_FILE_NAME = "pyproject.toml"


class GitFileAction(str, Enum):
    Skip = "skip"
    Create = "create"
    CreateAndPush = "create-and-push"


class HyperBaseMode(BaseModel):
    class Config:
        extra = "forbid"
        min_anystr_length = 1
        allow_mutation = False


class GitActions(HyperBaseMode):
    commit: GitFileAction = GitFileAction.Create
    branch: GitFileAction = GitFileAction.Skip
    tag: GitFileAction = GitFileAction.Skip


class Git(HyperBaseMode):
    remote: StrictStr = "origin"
    commit_format_pattern: StrictStr = (
        f"Bump version: {{{keys.CURRENT_VERSION}}} → {{{keys.NEW_VERSION}}}"
    )
    branch_format_pattern: StrictStr = f"bump_version_to_{{{keys.NEW_VERSION}}}"
    tag_format_pattern: StrictStr = f"v{{{keys.NEW_VERSION}}}"
    actions: GitActions = GitActions()


class File(HyperBaseMode):
    file_glob: StrictStr  # relative to project root directory
    keystone: StrictBool = False
    search_format_pattern: StrictStr = keys.VERSION
    replace_format_pattern: Optional[StrictStr] = None


HyperConfigFileValues = dict[str, Union[list[File], Optional[StrictStr], Git]]


class ConfigFile(HyperBaseMode):
    files: list[File] = Field(..., min_items=1)
    current_version: Optional[StrictStr] = None
    git: Git = Git()

    @root_validator(skip_on_failure=True)
    def check_keystone_files(
        cls,
        values: HyperConfigFileValues,
    ) -> HyperConfigFileValues:
        files = cast(list[File], values["files"])
        keystone_file_count = sum(1 for file in files if file.keystone)
        if keystone_file_count > 1:
            raise ValueError("Only one file is allowed to be a keystone file")
        current_version = values.get("current_version")
        if current_version is None:
            if keystone_file_count == 0:
                raise ValueError(
                    "current_version must be set if there is not a keystone file"
                )
        elif keystone_file_count != 0:
            raise ValueError(
                "Configuration can't specify the current_version while also having a keystone file"
            )
        return values


class ConfigVersionUpdater:
    def __init__(
        self,
        config_file: Path,
        full_document: TOMLDocument,
        config_table: TOMLDocument,
    ) -> None:
        """
        Initialize instance.

        :param config_file: File to write updated contents to.
        :param full_document: Config document to be written to file. Possibly including other
            values beyond what is used for this program.
        :param config_table: Config document with only the values used for this program.
        """
        self._config_file = config_file
        self._full_document = full_document
        self._config_table = config_table

    def __call__(self, new_version: Version) -> None:
        """
        Write the new version back to the configuration file.

        :param new_version: Version that should be stored in the configuration file.
        :raises ConfigurationFileWriteError: An error occurred writing out the configuration file.
        """

        self._config_table["current_version"] = str(new_version)
        try:
            self._config_file.write_text(tomlkit.dumps(self._full_document))
        except OSError as ex:
            raise ConfigurationFileWriteError(self._config_file, ex)


ConfigReadResult: TypeAlias = tuple[ConfigFile, Optional[ConfigVersionUpdater]]


def read_config(config_file: Optional[Path], project_root: Path) -> ConfigReadResult:
    """
    Read the appropriate configuration file.

    If `config_file` is given, that will be used as the dedicated configuration file to read.
    If `config_file` is not given, look for a configuration file in the project root. First check for a dedicated
    configuration file. If that doesn't exist, try pyproject.toml.

    :param config_file: Hyper config file to read from.
    :param project_root: Directory to look for a configuration file.
    :return: Parsed configuration content and an object that can be used to update the version
        stored in the configuration file. If the configuration uses a keystone file, this second
        values will be `None`.
    :raises ConfigurationError: No file was found or there was some error in the file.
    """
    if config_file is not None:
        return read_hyper_config(config_file)

    hyper_config_file = project_root / HYPER_CONFIG_FILE_NAME
    if hyper_config_file.exists():
        return read_hyper_config(hyper_config_file)

    pyproject_config_file = project_root / PYPROJECT_FILE_NAME
    if pyproject_config_file.exists():
        return read_pyproject_config(pyproject_config_file)

    raise ConfigurationFileNotFoundError(project_root)


def read_pyproject_config(
    pyproject_file: Path,
) -> ConfigReadResult:
    """
    Read configuration from pyproject file.

    :param pyproject_file: Path to the file to read.
    :return: Parsed configuration content and an object that can be used to update the version
        stored in the configuration file. If the configuration uses a keystone file, this second
        values will be `None`.
    :raises ConfigurationError: Some error exists in the configuration file.
    """
    return _read_config(pyproject_file, PYPROJECT_SUB_TABLE_KEYS)


def read_hyper_config(
    hyper_config_file: Path,
) -> ConfigReadResult:
    """
    Read configuration from pyproject file.

    :param hyper_config_file: Path to the decided configuration file to read.
    :return: Parsed configuration content and an object that can be used to update the version
        stored in the configuration file. If the configuration uses a keystone file, this second
        values will be `None`.
    :raises ConfigurationError: Some error exists in the configuration file.
    """
    return _read_config(hyper_config_file, [ROOT_TABLE_KEY])


def _read_config(config_file: Path, sub_tables: Sequence[str]) -> ConfigReadResult:
    try:
        full_document = tomlkit.parse(config_file.read_text())
    except (OSError, TOMLKitError) as ex:
        raise ConfigurationFileReadError(config_file, ex) from ex
    config_table = full_document
    for key in sub_tables:
        config_table = config_table.get(key)
        if config_table is None:
            raise SubTableNotExistError(config_file, PYPROJECT_SUB_TABLE_KEYS)

    try:
        config = ConfigFile(**config_table)
    except ValidationError as ex:
        raise InvalidConfigurationError(config_file, ex)

    if config.current_version is None:
        # uses keystone file & doesn't need to write back to pyproject file.
        return config, None
    return config, ConfigVersionUpdater(config_file, full_document, config_table)
