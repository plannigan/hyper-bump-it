"""
Bump version by part command.
"""
from pathlib import Path
from typing import Optional

import typer

from hyper_bump_it import _core as core
from hyper_bump_it._cli import common
from hyper_bump_it._config import BumpByArgs, BumpPart, GitAction, config_for_bump_by


def by(
    part_to_bump: BumpPart = typer.Argument(
        ..., help="Part of version to increment", show_default=False
    ),
    config_file: Optional[Path] = common.CONFIG_FILE,
    project_root: Path = common.PROJECT_ROOT,
    dry_run: bool = common.DRY_RUN,
    skip_confirm_prompt: Optional[bool] = common.SKIP_CONFIRM_PROMPT,
    current_version: Optional[str] = common.CURRENT_VERSION,
    commit: Optional[GitAction] = common.COMMIT,
    branch: Optional[GitAction] = common.BRANCH,
    tag: Optional[GitAction] = common.TAG,
    remote: Optional[str] = common.REMOTE,
    commit_format_pattern: Optional[str] = common.COMMIT_FORMAT_PATTERN,
    branch_format_pattern: Optional[str] = common.BRANCH_FORMAT_PATTERN,
    tag_format_pattern: Optional[str] = common.TAG_FORMAT_PATTERN,
) -> None:
    """
    Bump the version to the next value by a specific version part.
    """
    current_version_parsed = common.parse_version(current_version, "--current-version")

    with common.handle_bump_errors():
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
