"""
Initialize configuration command.
"""
from pathlib import Path
from typing import Mapping

import tomlkit
import typer
from pydantic import ValidationError
from rich import print
from tomlkit.exceptions import TOMLKitError

from hyper_bump_it._cli import common, interactive
from hyper_bump_it._config import (
    DEFAULT_BRANCH_ACTION,
    DEFAULT_BRANCH_FORMAT_PATTERN,
    DEFAULT_COMMIT_ACTION,
    DEFAULT_COMMIT_FORMAT_PATTERN,
    DEFAULT_REMOTE,
    DEFAULT_TAG_ACTION,
    DEFAULT_TAG_FORMAT_PATTERN,
    HYPER_CONFIG_FILE_NAME,
    PYPROJECT_FILE_NAME,
    PYPROJECT_SUB_TABLE_KEYS,
    ROOT_TABLE_KEY,
    ConfigFile,
    FileDefinition,
    GitAction,
    GitActionsConfigFile,
    GitConfigFile,
)
from hyper_bump_it._error import ConfigurationFileReadError, first_error_message

GIT_PANEL_NAME = "Git Configuration Options"


def init_command(
    current_version: str = typer.Argument(
        ..., help="Current version for the project", show_default=False
    ),
    config_file_name: str = typer.Option(
        HYPER_CONFIG_FILE_NAME,
        help="Custom file name for dedicated configuration file",
    ),
    project_root: Path = common.PROJECT_ROOT,
    pyproject: bool = typer.Option(
        False,
        help=f"Write config to {PYPROJECT_FILE_NAME}",
        show_default="Use dedicated configuration file",  # type: ignore[arg-type]
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive/--interactive",
        help="Write out a configuration without prompting for additional information "
        "(will need manual edits)",
    ),
    commit: GitAction = common.commit(DEFAULT_COMMIT_ACTION.value, GIT_PANEL_NAME),
    branch: GitAction = common.branch(DEFAULT_BRANCH_ACTION.value, GIT_PANEL_NAME),
    tag: GitAction = common.tag(DEFAULT_TAG_ACTION.value, GIT_PANEL_NAME),
    remote: str = common.remote(DEFAULT_REMOTE, GIT_PANEL_NAME),
    commit_format_pattern: str = common.commit_format_pattern(
        DEFAULT_COMMIT_FORMAT_PATTERN, GIT_PANEL_NAME
    ),
    branch_format_pattern: str = common.branch_format_pattern(
        DEFAULT_BRANCH_FORMAT_PATTERN, GIT_PANEL_NAME
    ),
    tag_format_pattern: str = common.tag_format_pattern(
        DEFAULT_TAG_FORMAT_PATTERN, GIT_PANEL_NAME
    ),
) -> None:
    version = common.parse_version(current_version, "CURRENT_VERSION")
    try:
        actions = GitActionsConfigFile(commit=commit, branch=branch, tag=tag)
    except ValidationError as ex:
        common.display_and_exit(first_error_message(ex), exit_code=2)

    config = ConfigFile(
        current_version=version,
        files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
        git=GitConfigFile(
            remote=remote,
            commit_format_pattern=commit_format_pattern,
            branch_format_pattern=branch_format_pattern,
            tag_format_pattern=tag_format_pattern,
            actions=actions,
        ),
    )
    with common.handle_bump_errors():
        if non_interactive:
            print(
                "Non-interactive mode: "
                "A sample configuration will be written that will need manual edits"
            )
        else:
            config, pyproject = interactive.config_update(
                config, pyproject, project_root
            )

        if pyproject:
            _write_pyproject_config(config, project_root)
        else:
            _write_dedicated_config(config, project_root / config_file_name)


def _write_pyproject_config(config: ConfigFile, project_root: Path) -> None:
    config_file = project_root / PYPROJECT_FILE_NAME
    if config_file.exists():
        try:
            full_document = tomlkit.parse(config_file.read_text())
        except (OSError, TOMLKitError) as ex:
            raise ConfigurationFileReadError(config_file, ex) from ex
    else:
        full_document = tomlkit.TOMLDocument()
    tool_table = full_document.setdefault(PYPROJECT_SUB_TABLE_KEYS[0], tomlkit.table())
    tool_table.update(_config_to_dict(config))
    _write_config(full_document, config_file)


def _write_dedicated_config(config: ConfigFile, config_file: Path) -> None:
    _write_config(_config_to_dict(config), config_file)


def _write_config(config: Mapping, config_file: Path) -> None:  # type: ignore[type-arg]
    config_file.write_text(tomlkit.dumps(config))


def _config_to_dict(config: ConfigFile) -> dict:  # type: ignore[type-arg]
    config_dict = config.dict(exclude_defaults=True)
    if config.current_version is not None:
        config_dict["current_version"] = str(config.current_version)
    return {ROOT_TABLE_KEY: config_dict}
