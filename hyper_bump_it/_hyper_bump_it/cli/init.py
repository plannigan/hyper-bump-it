"""
Initialize configuration command.
"""
from pathlib import Path
from typing import Annotated, Mapping

import tomlkit
import typer
from pydantic import ValidationError
from tomlkit.exceptions import TOMLKitError

from .. import ui
from ..config import (
    DEFAULT_ALLOWED_INITIAL_BRANCHES,
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
from ..error import ConfigurationFileReadError, first_error_message
from ..version import Version
from . import common, interactive

GIT_PANEL_NAME = "Git Configuration Options"


def init_command(
    current_version: Annotated[
        Version,
        typer.Argument(
            help="Current version for the project",
            show_default=False,
            parser=Version.parse,
        ),
    ],
    config_file_name: Annotated[
        str,
        typer.Option(
            help="Custom file name for dedicated configuration file",
        ),
    ] = HYPER_CONFIG_FILE_NAME,
    project_root: Annotated[Path, common.PROJECT_ROOT] = common.PROJECT_ROOT_DEFAULT,
    pyproject: Annotated[
        bool,
        typer.Option(
            help=f"Write config to {PYPROJECT_FILE_NAME}",
            show_default="Use dedicated configuration file",
        ),
    ] = False,
    non_interactive: Annotated[
        bool,
        typer.Option(
            "--non-interactive/--interactive",
            help="Write out a configuration without prompting for additional information "
            "(will need manual edits)",
        ),
    ] = False,
    commit: Annotated[
        GitAction, common.commit(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_COMMIT_ACTION,
    branch: Annotated[
        GitAction, common.branch(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_BRANCH_ACTION,
    tag: Annotated[
        GitAction, common.tag(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_TAG_ACTION,
    remote: Annotated[
        str, common.remote(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_REMOTE,
    commit_format_pattern: Annotated[
        str, common.commit_format_pattern(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_COMMIT_FORMAT_PATTERN,
    branch_format_pattern: Annotated[
        str, common.branch_format_pattern(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_BRANCH_FORMAT_PATTERN,
    tag_format_pattern: Annotated[
        str, common.tag_format_pattern(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_TAG_FORMAT_PATTERN,
    allowed_init_branch: Annotated[
        list[str], common.allowed_init_branch(GIT_PANEL_NAME, show_default=True)
    ] = list(DEFAULT_ALLOWED_INITIAL_BRANCHES),
    allow_any_init_branch: Annotated[
        bool, common.allow_any_init_branch(GIT_PANEL_NAME)
    ] = False,
) -> None:
    try:
        actions = GitActionsConfigFile(commit=commit, branch=branch, tag=tag)
    except ValidationError as ex:
        common.display_and_exit(first_error_message(ex), exit_code=2)

    if allow_any_init_branch:
        allowed_init_branch = []

    project_root = common.resolve(project_root)
    config = ConfigFile(
        current_version=current_version,
        files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
        git=GitConfigFile(
            remote=remote,
            commit_format_pattern=commit_format_pattern,
            branch_format_pattern=branch_format_pattern,
            tag_format_pattern=tag_format_pattern,
            allowed_initial_branches=frozenset(allowed_init_branch),
            actions=actions,
        ),
    )
    with common.handle_bump_errors():
        if non_interactive:
            ui.display(
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
    _git_branch_set_to_list(config_dict, "allowed_initial_branches")
    _git_branch_set_to_list(config_dict, "extend_allowed_initial_branches")
    return {ROOT_TABLE_KEY: config_dict}


def _git_branch_set_to_list(config_dict: dict, git_key: str) -> None:  # type: ignore[type-arg]
    git_config = config_dict.get("git")
    if git_config is None:
        return
    value = git_config.get(git_key)
    if value is not None:
        git_config[git_key] = list(value)
