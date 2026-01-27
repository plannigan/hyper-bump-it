"""
Bump version by part command.
"""

from pathlib import Path
from typing import Annotated

import typer

from .. import core
from ..config import BumpByArgs, BumpPart, GitAction, config_for_bump_by
from ..version import Version
from . import common


def by_command(
    part_to_bump: Annotated[
        BumpPart,
        typer.Argument(..., help="Part of version to increment", show_default=False),
    ],
    config_file: Annotated[
        Path | None, common.CONFIG_FILE
    ] = common.CONFIG_FILE_DEFAULT,
    project_root: Annotated[Path, common.PROJECT_ROOT] = common.PROJECT_ROOT_DEFAULT,
    dry_run: Annotated[bool, common.DRY_RUN] = common.DRY_RUN_DEFAULT,
    patch: Annotated[bool, common.PATCH] = common.PATCH_DEFAULT,
    skip_confirm_prompt: Annotated[
        bool | None, common.SKIP_CONFIRM_PROMPT
    ] = common.SKIP_CONFIRM_PROMPT_DEFAULT,
    current_version: Annotated[
        Version | None, common.CURRENT_VERSION
    ] = common.CURRENT_VERSION_DEFAULT,
    commit: Annotated[GitAction | None, common.commit()] = None,
    branch: Annotated[GitAction | None, common.branch()] = None,
    tag: Annotated[GitAction | None, common.tag()] = None,
    remote: Annotated[str | None, common.remote()] = None,
    commit_format_pattern: Annotated[str | None, common.commit_format_pattern()] = None,
    branch_format_pattern: Annotated[str | None, common.branch_format_pattern()] = None,
    tag_name_format_pattern: Annotated[
        str | None, common.tag_name_format_pattern()
    ] = None,
    tag_message_format_pattern: Annotated[
        str | None, common.tag_message_format_pattern()
    ] = None,
    allowed_init_branch: Annotated[
        list[str] | None, common.allowed_init_branch()
    ] = None,
    allow_any_init_branch: Annotated[
        bool | None, common.allow_any_init_branch()
    ] = None,
) -> None:
    """
    Bump the version to the next value by a specific version part.
    """
    with common.handle_bump_errors():
        app_config = config_for_bump_by(
            BumpByArgs(
                part_to_bump,
                config_file=common.resolve(config_file),
                project_root=common.resolve(project_root),
                dry_run=dry_run,
                patch=patch,
                skip_confirm_prompt=skip_confirm_prompt,
                current_version=current_version,
                commit=commit,
                branch=branch,
                tag=tag,
                remote=remote,
                commit_format_pattern=commit_format_pattern,
                branch_format_pattern=branch_format_pattern,
                tag_name_format_pattern=tag_name_format_pattern,
                tag_message_format_pattern=tag_message_format_pattern,
                allowed_initial_branches=common.allowed_init_branches(
                    allowed_init_branch, allow_any_init_branch
                ),
            )
        )

        core.do_bump(app_config)
