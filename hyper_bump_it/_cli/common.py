"""
Common command line functionality.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, overload

import typer
from rich import print
from rich.align import AlignMethod
from rich.panel import Panel
from semantic_version import Version

from hyper_bump_it._error import BumpItError

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


@overload
def parse_version(version: str, parameter_name: str) -> Version:
    ...


@overload
def parse_version(version: Optional[str], parameter_name: str) -> Optional[Version]:
    ...


def parse_version(version: Optional[str], parameter_name: str) -> Optional[Version]:
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
def handle_bump_errors() -> Iterator[None]:
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
