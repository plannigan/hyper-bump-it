"""
Common command line functionality.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, NoReturn, Optional, Protocol, overload

import typer
from rich.align import AlignMethod

from .. import ui
from ..error import BumpItError
from ..version import Version

OVERRIDE_PANEL_NAME = "Configuration File Override"
# These values match what typer uses
ERROR_PANEL_NAME = "Error"
ERROR_PANEL_BORDER_STYLE = "red"
ERROR_PANEL_TILE_ALIGN_: AlignMethod = "left"
EXAMPLE_FILE_GLOB = "version.txt"


class OptionFactory(Protocol):
    def __call__(  # type: ignore[misc]
        self, panel_name: str = ..., show_default: bool = ...
    ) -> Any:
        ...


def _create_option_factory(description: str, *param_decls: str) -> OptionFactory:
    def _create_option(  # type: ignore[misc]
        panel_name: str = OVERRIDE_PANEL_NAME, show_default: bool = False
    ) -> Any:
        return typer.Option(
            *param_decls,
            help=description,
            show_default=show_default,
            rich_help_panel=panel_name,
        )

    return _create_option


CONFIG_FILE = typer.Option(
    help="Path to dedicated configuration file to use instead of normal file discovery",
    show_default=False,
)
CONFIG_FILE_DEFAULT: Optional[Path] = None
PROJECT_ROOT = typer.Option(  # type: ignore[call-overload]
    help="Path to directory containing the project",
    show_default="Use current directory",
)
PROJECT_ROOT_DEFAULT = Path.cwd()
DRY_RUN = typer.Option(
    "--no",
    "-n",
    "--dry-run/--no-dry-run",
    help="Answer no to the confirmation prompt. "
    "Only displaying the operations that would be performed",
    show_default=False,
)
DRY_RUN_DEFAULT = False
PATCH = typer.Option(
    "--patch/--no-patch",
    help="Like --dry-run, but only display the unified diff output for the planned changes",
    show_default=False,
)
PATCH_DEFAULT = False
SKIP_CONFIRM_PROMPT = typer.Option(
    "--yes/--interactive",
    "-y",
    help="Answer yes to the confirmation prompt and run non-interactively",
    show_default=False,
)
SKIP_CONFIRM_PROMPT_DEFAULT: Optional[bool] = None
CURRENT_VERSION = typer.Option(
    help="Override the current version",
    show_default=False,
    rich_help_panel=OVERRIDE_PANEL_NAME,
    parser=Version.parse,
)
CURRENT_VERSION_DEFAULT: Optional[Version] = None

commit = _create_option_factory("Control commit Git action")
branch = _create_option_factory("Control branch Git action")
tag = _create_option_factory("Control tag Git action")
remote = _create_option_factory("Name of remote to use when pushing changes")
commit_format_pattern = _create_option_factory(
    "Format pattern to use for commit message"
)
branch_format_pattern = _create_option_factory("Format pattern to use for branch name")
tag_format_pattern = _create_option_factory("Format pattern to use for tag name")
# Typer returns an empty tuple even when the default is None and the argument is annotated as Optional[list[str]]
# https://github.com/tiangolo/typer/issues/170
allowed_init_branch = _create_option_factory(
    "Name of allowed initial branch (can be used multiple times)"
)
allow_any_init_branch = _create_option_factory(
    "Disable any initial branch restrictions. (takes precedence over --allowed-init-branch)",
    "--allow-any-init-branch",
)


def allowed_init_branches(
    allowed_branches_arg: Optional[list[str]],
    allow_any_init_branch_arg: Optional[bool],
) -> Optional[frozenset[str]]:
    if allow_any_init_branch_arg is True:
        return frozenset()
    if allowed_branches_arg is None or len(allowed_branches_arg) == 0:
        return None

    unique_names = frozenset(allowed_branches_arg)
    if len(unique_names) == len(allowed_branches_arg):
        return unique_names

    for value in unique_names:
        allowed_branches_arg.remove(value)

    remaining = "', '".join(sorted(set(allowed_branches_arg)))
    raise typer.BadParameter(
        f"'allowed-init-branch' should only be given unique values. Appeared more than once: '{remaining}'"
    )


@contextmanager
def handle_bump_errors() -> Iterator[None]:
    try:
        yield
    except BumpItError as ex:
        display_and_exit(ex)


def display_and_exit(message: ui.PanelMessage, exit_code: int = 1) -> NoReturn:
    ui.panel(
        message,
        border_style="red",
        title="Error",
    )
    raise typer.Exit(exit_code)


@overload
def resolve(path: Path) -> Path:
    ...


@overload
def resolve(path: Optional[Path]) -> Optional[Path]:
    ...


def resolve(path: Optional[Path]) -> Optional[Path]:
    return None if path is None else path.resolve()
