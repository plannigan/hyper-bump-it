"""
Bump to version command.
"""
from pathlib import Path
from typing import Optional

import typer

from hyper_bump_it import _core as core
from hyper_bump_it._cli import common
from hyper_bump_it._config import BumpToArgs, GitAction, config_for_bump_to


def to_command(
    new_version: str = typer.Argument(
        ..., help="The new version to bump to", show_default=False
    ),
    config_file: Optional[Path] = common.CONFIG_FILE,
    project_root: Path = common.PROJECT_ROOT,
    dry_run: bool = common.DRY_RUN,
    skip_confirm_prompt: Optional[bool] = common.SKIP_CONFIRM_PROMPT,
    current_version: Optional[str] = common.CURRENT_VERSION,
    commit: Optional[GitAction] = common.commit(),
    branch: Optional[GitAction] = common.branch(),
    tag: Optional[GitAction] = common.tag(),
    remote: Optional[str] = common.remote(),
    commit_format_pattern: Optional[str] = common.commit_format_pattern(),
    branch_format_pattern: Optional[str] = common.branch_format_pattern(),
    tag_format_pattern: Optional[str] = common.tag_format_pattern(),
) -> None:
    """
    Bump the version to a specific version.
    """
    new_version_parsed = common.parse_version(new_version, "NEW_VERSION")
    current_version_parsed = common.parse_version(current_version, "--current-version")

    with common.handle_bump_errors():
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
