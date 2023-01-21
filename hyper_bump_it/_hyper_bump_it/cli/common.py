"""
Common command line functionality.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, NoReturn, Optional, Protocol, overload

import typer
from rich import print
from rich.align import AlignMethod
from rich.console import RenderableType
from rich.panel import Panel

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
        self, default: object = ..., panel_name: str = ...
    ) -> Any:
        ...


def _create_option_factory(description: str, *param_decls: str) -> OptionFactory:
    def _create_option(  # type: ignore[misc]
        default: object = None, panel_name: str = OVERRIDE_PANEL_NAME
    ) -> Any:
        return typer.Option(
            default,
            *param_decls,
            help=description,
            show_default=default is not None,
            rich_help_panel=panel_name,
        )

    return _create_option


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
            return Version.parse(version)
        except ValueError:
            raise typer.BadParameter(
                f"'{version}' is not a valid version", param_hint=parameter_name
            )


def allowed_init_branches(
    allowed_branches_arg: list[str],
    allow_any_init_branch_arg: Optional[bool],
) -> Optional[frozenset[str]]:
    if allow_any_init_branch_arg is True:
        return frozenset()
    if len(allowed_branches_arg) == 0:
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


def display_and_exit(message: RenderableType, exit_code: int = 1) -> NoReturn:
    print(
        Panel(
            message,
            border_style="red",
            title="Error",
            title_align="left",
            highlight=True,
        )
    )
    raise typer.Exit(exit_code)
