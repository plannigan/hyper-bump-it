from pathlib import Path
from typing import Optional, overload

import typer
from semantic_version import Version

from hyper_bump_it import _core as core
from hyper_bump_it._config import (
    BumpByArgs,
    BumpPart,
    BumpToArgs,
    GitAction,
    config_for_bump_by,
    config_for_bump_to,
)

app = typer.Typer()

OVERRIDE_PANEL_NAME = "Configuration File Override"

CONFIG_FILE = typer.Option(
    None,
    help="Path to dedicated configuration file to use instead of normal file discovery",
    show_default=False,
)
PROJECT_ROOT = typer.Option(
    Path.cwd(),
    help="Path to directory containing the project",
    show_default="Use current directory",  # type: ignore[arg-type]
)
DRY_RUN = typer.Option(
    False,
    help="Only display the operations that would be performed",
    show_default=False,
)
CURRENT_VERSION = typer.Option(
    None,
    help="Override the current version",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
COMMIT = typer.Option(
    None,
    help="Control commit Git action",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
BRANCH = typer.Option(
    None,
    help="Control branch Git action",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
TAG = typer.Option(
    None,
    help="Control tag Git action",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
REMOTE = typer.Option(
    None,
    help="Name of remote to use when pushing changes",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
COMMIT_FORMAT_PATTERN = typer.Option(
    None,
    help="Format pattern to use for commit message",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
BRANCH_FORMAT_PATTERN = typer.Option(
    None,
    help="Format pattern to use for branch name",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)
TAG_FORMAT_PATTERN = typer.Option(
    None,
    help="Format pattern to use for tag name",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
)


@app.command()
def to(
    new_version: str = typer.Argument(
        ..., help="The new version to bump to", show_default=False
    ),
    config_file: Optional[Path] = CONFIG_FILE,
    project_root: Path = PROJECT_ROOT,
    dry_run: bool = DRY_RUN,
    current_version: Optional[str] = CURRENT_VERSION,
    commit: Optional[GitAction] = COMMIT,
    branch: Optional[GitAction] = BRANCH,
    tag: Optional[GitAction] = TAG,
    remote: Optional[str] = REMOTE,
    commit_format_pattern: Optional[str] = COMMIT_FORMAT_PATTERN,
    branch_format_pattern: Optional[str] = BRANCH_FORMAT_PATTERN,
    tag_format_pattern: Optional[str] = TAG_FORMAT_PATTERN,
) -> None:
    """
    Bump the version to a specific version.
    """
    new_version_parsed = _parse_version(new_version, "NEW_VERSION")
    current_version_parsed = _parse_version(current_version, "--current-version")

    app_config = config_for_bump_to(
        BumpToArgs(
            new_version=new_version_parsed,
            config_file=config_file,
            project_root=project_root,
            dry_run=dry_run,
            current_version=current_version_parsed,
            commit=commit,
            branch=branch,
            tag=tag,
            remote=remote,
            commit_format_pattern=commit_format_pattern,
            branch_format_pattern=branch_format_pattern,
            tag_format_pattern=tag_format_pattern,
        )
    )

    core.do_bump(app_config)


@app.command()
def by(
    part_to_bump: BumpPart = typer.Argument(
        ..., help="Part of version to increment", show_default=False
    ),
    config_file: Optional[Path] = CONFIG_FILE,
    project_root: Path = PROJECT_ROOT,
    dry_run: bool = DRY_RUN,
    current_version: Optional[str] = CURRENT_VERSION,
    commit: Optional[GitAction] = COMMIT,
    branch: Optional[GitAction] = BRANCH,
    tag: Optional[GitAction] = TAG,
    remote: Optional[str] = REMOTE,
    commit_format_pattern: Optional[str] = COMMIT_FORMAT_PATTERN,
    branch_format_pattern: Optional[str] = BRANCH_FORMAT_PATTERN,
    tag_format_pattern: Optional[str] = TAG_FORMAT_PATTERN,
) -> None:
    """
    Bump the version to the next value by a specific version part.
    """
    current_version_parsed = _parse_version(current_version, "--current-version")

    app_config = config_for_bump_by(
        BumpByArgs(
            part_to_bump,
            config_file=config_file,
            project_root=project_root,
            dry_run=dry_run,
            current_version=current_version_parsed,
            commit=commit,
            branch=branch,
            tag=tag,
            remote=remote,
            commit_format_pattern=commit_format_pattern,
            branch_format_pattern=branch_format_pattern,
            tag_format_pattern=tag_format_pattern,
        )
    )

    core.do_bump(app_config)


@overload
def _parse_version(version: str, parameter_name: str) -> Version:
    ...


@overload
def _parse_version(version: Optional[str], parameter_name: str) -> Optional[Version]:
    ...


def _parse_version(version: Optional[str], parameter_name: str) -> Optional[Version]:
    if version is None:
        return None
    else:
        try:
            return Version(version)
        except ValueError:
            raise typer.BadParameter(
                f"'{version}' is not a valid version", param_hint=parameter_name
            )
