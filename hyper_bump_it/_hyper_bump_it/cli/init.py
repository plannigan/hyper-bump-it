"""
Initialize configuration command.
"""
from pathlib import Path
from typing import Annotated, Mapping

import tomlkit
import typer
from pydantic import ValidationError
from rich.text import Text
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
    DEFAULT_TAG_NAME_FORMAT_PATTERN,
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
from ..error import (
    ConfigurationAlreadyExistsError,
    ConfigurationFileReadError,
    first_error_message,
)
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
    tag_name_format_pattern: Annotated[
        str, common.tag_name_format_pattern(GIT_PANEL_NAME, show_default=True)
    ] = DEFAULT_TAG_NAME_FORMAT_PATTERN,
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
            tag_name_format_pattern=tag_name_format_pattern,
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

        try:
            if pyproject:
                _maybe_write_pyproject_config(config, project_root, non_interactive)
            else:
                _maybe_write_dedicated_config(
                    config, project_root / config_file_name, non_interactive
                )
        except ConfigurationAlreadyExistsError as ex:
            common.display_and_exit(ex)


def _maybe_write_pyproject_config(
    config: ConfigFile, project_root: Path, non_interactive: bool
) -> None:
    config_file = project_root / PYPROJECT_FILE_NAME
    if not config_file.exists():
        # no need to existing config check
        full_document = tomlkit.TOMLDocument()
        _write_pyproject_config(config, config_file, full_document)
        return

    try:
        full_document = tomlkit.parse(config_file.read_text())
    except (OSError, TOMLKitError) as ex:
        raise ConfigurationFileReadError(config_file, ex) from ex

    if _pyproject_has_config(full_document):
        if non_interactive:
            raise ConfigurationAlreadyExistsError(config_file)

        if not _confirm_overwrite(config_file, "already has a"):
            raise ConfigurationAlreadyExistsError(config_file)

    _write_pyproject_config(config, config_file, full_document)


def _pyproject_has_config(pyproject_config: tomlkit.TOMLDocument) -> bool:
    tool_table = pyproject_config.get(PYPROJECT_SUB_TABLE_KEYS[0])
    return tool_table is not None and tool_table.get(ROOT_TABLE_KEY) is not None


def _write_pyproject_config(
    config: ConfigFile, config_file: Path, full_document: tomlkit.TOMLDocument
) -> None:
    # ensure tool table exists
    tool_table = full_document.setdefault(PYPROJECT_SUB_TABLE_KEYS[0], tomlkit.table())
    tool_table.update(_config_to_dict(config))
    _write_config(full_document, config_file)


def _maybe_write_dedicated_config(
    config: ConfigFile, config_file: Path, non_interactive: bool
) -> None:
    if config_file.exists():
        if non_interactive:
            raise ConfigurationAlreadyExistsError(config_file)
        if not _confirm_overwrite(config_file, "already exists as a"):
            raise ConfigurationAlreadyExistsError(config_file)

    _write_config(_config_to_dict(config), config_file)


def _confirm_overwrite(config_file: Path, issue_message: str) -> bool:
    return ui.confirm(
        Text()
        .append(str(config_file), style="file.path")
        .append(f" {issue_message} ")
        .append("hyper-bump-it", style="app")
        .append(" configuration. Do you want to overwrite it?"),
        default=False,
    )


def _write_config(config: Mapping[str, object], config_file: Path) -> None:
    config_file.write_text(tomlkit.dumps(config))


def _config_to_dict(config: ConfigFile) -> Mapping[str, object]:
    config_dict = config.model_dump(exclude_defaults=True)
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
