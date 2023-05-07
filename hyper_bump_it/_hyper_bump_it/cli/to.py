"""
Bump to version command.
"""
from pathlib import Path
from typing import Annotated, Optional

import typer

from .. import core
from ..config import BumpToArgs, GitAction, config_for_bump_to
from ..version import Version
from . import common


def to_command(
    new_version: Annotated[
        Version,
        typer.Argument(
            ...,
            help="The new version to bump to",
            show_default=False,
            parser=Version.parse,
        ),
    ],
    config_file: Annotated[
        Optional[Path], common.CONFIG_FILE
    ] = common.CONFIG_FILE_DEFAULT,
    project_root: Annotated[Path, common.PROJECT_ROOT] = common.PROJECT_ROOT_DEFAULT,
    dry_run: Annotated[bool, common.DRY_RUN] = common.DRY_RUN_DEFAULT,
    patch: Annotated[bool, common.PATCH] = common.PATCH_DEFAULT,
    skip_confirm_prompt: Annotated[
        Optional[bool], common.SKIP_CONFIRM_PROMPT
    ] = common.SKIP_CONFIRM_PROMPT_DEFAULT,
    current_version: Annotated[
        Optional[Version], common.CURRENT_VERSION
    ] = common.CURRENT_VERSION_DEFAULT,
    commit: Annotated[Optional[GitAction], common.commit()] = None,
    branch: Annotated[Optional[GitAction], common.branch()] = None,
    tag: Annotated[Optional[GitAction], common.tag()] = None,
    remote: Annotated[Optional[str], common.remote()] = None,
    commit_format_pattern: Annotated[
        Optional[str], common.commit_format_pattern()
    ] = None,
    branch_format_pattern: Annotated[
        Optional[str], common.branch_format_pattern()
    ] = None,
    tag_format_pattern: Annotated[Optional[str], common.tag_format_pattern()] = None,
    allowed_init_branch: Annotated[
        Optional[list[str]], common.allowed_init_branch()
    ] = None,
    allow_any_init_branch: Annotated[
        Optional[bool], common.allow_any_init_branch()
    ] = None,
) -> None:
    """
    Bump the version to a specific version.
    """
    with common.handle_bump_errors():
        app_config = config_for_bump_to(
            BumpToArgs(
                new_version=new_version,
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
                tag_format_pattern=tag_format_pattern,
                allowed_initial_branches=common.allowed_init_branches(
                    allowed_init_branch, allow_any_init_branch
                ),
            )
        )

        core.do_bump(app_config)
