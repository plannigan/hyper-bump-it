from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, overload

import typer
from rich import print
from rich.align import AlignMethod
from rich.panel import Panel
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
from hyper_bump_it._error import BumpItError

app = typer.Typer()

OVERRIDE_PANEL_NAME = "Configuration File Override"
# These values match what typer uses
ERROR_PANEL_NAME = "Error"
ERROR_PANEL_BORDER_STYLE = "red"
ERROR_PANEL_TILE_ALIGN_: AlignMethod = "left"


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
    "--no",
    "-n",
    "--dry-run/--no-dry-run",
    help="Answer no to the confirmation prompt. "
    "Only displaying the operations that would be performed",
    show_default=False,
)
SKIP_CONFIRM_PROMPT = typer.Option(
    None,
    "--yes/--interactive",
    "-y",
    help="Answer yes to the confirmation prompt and run non-interactively",
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
    skip_confirm_prompt: Optional[bool] = SKIP_CONFIRM_PROMPT,
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

    with _handle_bump_errors():
        app_config = config_for_bump_to(
            BumpToArgs(
                new_version=new_version_parsed,
                config_file=config_file,
                project_root=project_root,
                dry_run=dry_run,
                skip_confirm_prompt=skip_confirm_prompt,
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
    skip_confirm_prompt: Optional[bool] = SKIP_CONFIRM_PROMPT,
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

    with _handle_bump_errors():
        app_config = config_for_bump_by(
            BumpByArgs(
                part_to_bump,
                config_file=config_file,
                project_root=project_root,
                dry_run=dry_run,
                skip_confirm_prompt=skip_confirm_prompt,
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


@contextmanager
def _handle_bump_errors() -> Iterator[None]:
    try:
        yield
    except BumpItError as ex:
        print(
            Panel(
                ex,
                border_style="red",
                title="Error",
                title_align="left",
                highlight=True,
            )
        )
        raise typer.Exit(1)
