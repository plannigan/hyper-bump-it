"""
Common test data that can be used across multiple test cases.
"""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from textwrap import dedent
from typing import Optional

from git import Repo
from semantic_version import Version
from tomlkit import TOMLDocument

from hyper_bump_it._config import (
    BumpByArgs,
    BumpPart,
    BumpToArgs,
    Config,
    File,
    Git,
    GitAction,
    GitActions,
)
from hyper_bump_it._config.file import ConfigVersionUpdater
from hyper_bump_it._files import PlannedChange
from hyper_bump_it._git import GitOperationsInfo
from hyper_bump_it._text_formatter import TextFormatter, keys

ALL_KEYS = tuple(getattr(keys, name) for name in dir(keys) if not name.startswith("__"))

SOME_DATE = date(year=2022, month=10, day=19)
SOME_MAJOR = 1
SOME_MINOR = 2
SOME_PATCH = 3
SOME_PRERELEASE = "11.22"
SOME_BUILD = "b123.321"
SOME_VERSION = Version(
    major=SOME_MAJOR,
    minor=SOME_MINOR,
    patch=SOME_PATCH,
    prerelease=SOME_PRERELEASE.split("."),
    build=SOME_BUILD.split("."),
)
SOME_VERSION_STRING = str(SOME_VERSION)
SOME_OTHER_MAJOR = 4
SOME_OTHER_MINOR = 5
SOME_OTHER_PATCH = 6
SOME_OTHER_PRERELEASE = "33.44"
SOME_OTHER_BUILD = "b456.654"
SOME_OTHER_VERSION = Version(
    major=SOME_OTHER_MAJOR,
    minor=SOME_OTHER_MINOR,
    patch=SOME_OTHER_PATCH,
    prerelease=SOME_OTHER_PRERELEASE.split("."),
    build=SOME_OTHER_BUILD.split("."),
)
SOME_OTHER_VERSION_STRING = str(SOME_OTHER_VERSION)
SOME_OTHER_PARTIAL_VERSION = Version(
    major=SOME_OTHER_MAJOR,
    minor=SOME_OTHER_MINOR,
    patch=SOME_OTHER_PATCH,
)
SOME_OTHER_PARTIAL_VERSION_STRING = str(SOME_OTHER_PARTIAL_VERSION)
SOME_BUMP_PART = BumpPart.Minor
SOME_CONFIG_FILE_NAME = "config.toml"
SOME_DIRECTORY_NAME = "test-dir"


def some_text_formatter(
    current_version: Version = SOME_VERSION,
    new_version: Version = SOME_OTHER_VERSION,
    today: date = SOME_DATE,
) -> TextFormatter:
    return TextFormatter(current_version, new_version, today)


SOME_REMOTE = "test-remote"
SOME_COMMIT_MESSAGE = "test commit message"
SOME_BRANCH = "test-branch"
SOME_TAG = "test-tag"
SOME_COMMIT_PATTERN = f"test commit {{{keys.NEW_VERSION}}}"
SOME_BRANCH_PATTERN = f"test-branch-{{{keys.NEW_VERSION}}}"
SOME_TAG_PATTERN = f"test-tag-{{{keys.NEW_VERSION}}}"

SOME_COMMIT_ACTION = GitAction.CreateAndPush
SOME_BRANCH_ACTION = GitAction.Skip
SOME_TAG_ACTION = GitAction.Create
SOME_NON_GIT_ACTION_STRING = "other"

SOME_FILE_INDEX = 3
SOME_OLD_LINE = "start text"
SOME_NEW_LINE = "updated text"


def some_git_actions(
    commit=SOME_COMMIT_ACTION,
    branch=SOME_BRANCH_ACTION,
    tag=SOME_TAG_ACTION,
) -> GitActions:
    return GitActions(commit=commit, branch=branch, tag=tag)


def some_git(
    remote=SOME_REMOTE,
    commit_format_pattern=SOME_COMMIT_PATTERN,
    branch_format_pattern=SOME_BRANCH_PATTERN,
    tag_format_pattern=SOME_TAG_PATTERN,
    actions=some_git_actions(),
) -> Git:
    return Git(
        remote=remote,
        commit_format_pattern=commit_format_pattern,
        branch_format_pattern=branch_format_pattern,
        tag_format_pattern=tag_format_pattern,
        actions=actions,
    )


SOME_FILE_GLOB = "foo*.txt"
SOME_GLOB_MATCHED_FILE_NAME = "foo-1.txt"
SOME_OTHER_GLOB_MATCHED_FILE_NAME = "foo-2.txt"
SOME_SEARCH_FORMAT_PATTERN = f"{{{keys.VERSION}}}"
SOME_REPLACE_FORMAT_PATTERN = f"{{{keys.NEW_VERSION}}}"


def some_file(
    file_glob=SOME_FILE_GLOB,
    search_format_pattern=SOME_SEARCH_FORMAT_PATTERN,
    replace_format_pattern=SOME_REPLACE_FORMAT_PATTERN,
) -> File:
    return File(
        file_glob=file_glob,
        search_format_pattern=search_format_pattern,
        replace_format_pattern=replace_format_pattern,
    )


def some_git_operations_info(
    remote=SOME_REMOTE,
    commit_message=SOME_COMMIT_MESSAGE,
    branch_name=SOME_BRANCH,
    tag_name=SOME_TAG,
    actions=some_git_actions(),
) -> GitOperationsInfo:
    return GitOperationsInfo(
        remote=remote,
        commit_message=commit_message,
        branch_name=branch_name,
        tag_name=tag_name,
        actions=actions,
    )


def some_minimal_config_text(table_root: str, version: Optional[str]) -> str:
    if version is None:
        current_version = ""
        keystone = "keystone = true"
    else:
        current_version = f'current_version = "{version}"'
        keystone = ""
    return dedent(
        f"""\
        [{table_root}]
        {current_version}
        [[{table_root}.files]]
        file_glob = "{SOME_FILE_GLOB}"
        {keystone}
"""
    )


def no_config_override_bump_to_args(
    project_root: Path,
    new_version: Version = SOME_OTHER_VERSION,
    config_file: Optional[Path] = None,
    dry_run: bool = False,
) -> BumpToArgs:
    return BumpToArgs(
        new_version=new_version,
        config_file=config_file,
        project_root=project_root,
        dry_run=dry_run,
        current_version=None,
        commit=None,
        branch=None,
        tag=None,
        remote=None,
        commit_format_pattern=None,
        branch_format_pattern=None,
        tag_format_pattern=None,
    )


def some_bump_to_args(
    project_root: Path,
    new_version: Version = SOME_OTHER_VERSION,
    config_file: Optional[Path] = None,
    dry_run: bool = False,
    current_version: Optional[Version] = SOME_OTHER_PARTIAL_VERSION,
    commit: Optional[GitAction] = SOME_COMMIT_ACTION,
    branch: Optional[GitAction] = SOME_BRANCH_ACTION,
    tag: Optional[GitAction] = SOME_TAG_ACTION,
    remote: Optional[str] = SOME_REMOTE,
    commit_format_pattern: Optional[str] = SOME_COMMIT_PATTERN,
    branch_format_pattern: Optional[str] = SOME_BRANCH_PATTERN,
    tag_format_pattern: Optional[str] = SOME_TAG_PATTERN,
) -> BumpToArgs:
    return BumpToArgs(
        new_version=new_version,
        config_file=config_file,
        project_root=project_root,
        dry_run=dry_run,
        current_version=current_version,
        commit=commit,
        branch=branch,
        tag=tag,
        remote=remote,
        commit_format_pattern=commit_format_pattern,
        branch_format_pattern=branch_format_pattern,
        tag_format_pattern=tag_format_pattern,
    )


def no_config_override_bump_by_args(
    project_root: Path,
    part_to_bump: BumpPart = SOME_BUMP_PART,
    config_file: Optional[Path] = None,
    dry_run: bool = False,
) -> BumpByArgs:
    return BumpByArgs(
        part_to_bump=part_to_bump,
        config_file=config_file,
        project_root=project_root,
        dry_run=dry_run,
        current_version=None,
        commit=None,
        branch=None,
        tag=None,
        remote=None,
        commit_format_pattern=None,
        branch_format_pattern=None,
        tag_format_pattern=None,
    )


def some_bump_by_args(
    project_root: Path,
    part_to_bump: BumpPart = SOME_BUMP_PART,
    config_file: Optional[Path] = None,
    dry_run: bool = False,
    current_version: Optional[Version] = SOME_OTHER_PARTIAL_VERSION,
    commit: Optional[GitAction] = SOME_COMMIT_ACTION,
    branch: Optional[GitAction] = SOME_BRANCH_ACTION,
    tag: Optional[GitAction] = SOME_TAG_ACTION,
    remote: Optional[str] = SOME_REMOTE,
    commit_format_pattern: Optional[str] = SOME_COMMIT_PATTERN,
    branch_format_pattern: Optional[str] = SOME_BRANCH_PATTERN,
    tag_format_pattern: Optional[str] = SOME_TAG_PATTERN,
) -> BumpByArgs:
    return BumpByArgs(
        part_to_bump=part_to_bump,
        config_file=config_file,
        project_root=project_root,
        dry_run=dry_run,
        current_version=current_version,
        commit=commit,
        branch=branch,
        tag=tag,
        remote=remote,
        commit_format_pattern=commit_format_pattern,
        branch_format_pattern=branch_format_pattern,
        tag_format_pattern=tag_format_pattern,
    )


class AnyConfigVersionUpdater(ConfigVersionUpdater):
    """A helper object that compares equal to any ConfigVersionUpdater instance."""

    def __init__(self):
        super().__init__(Path(), TOMLDocument(), TOMLDocument())

    def __eq__(self, other):
        return isinstance(other, ConfigVersionUpdater)

    def __ne__(self, other):
        return not isinstance(other, ConfigVersionUpdater)

    def __repr__(self):
        return "<AnyConfigVersionUpdater>"


def some_application_config(
    project_root: Path,
    current_version: Version = SOME_VERSION,
    new_version: Version = SOME_OTHER_VERSION,
    files: Optional[list[File]] = None,
    git: Git = some_git(),
    dry_run: bool = False,
    config_version_updater: Optional[ConfigVersionUpdater] = AnyConfigVersionUpdater(),
) -> Config:
    if files is None:
        files = [some_file()]
    return Config(
        current_version=current_version,
        new_version=new_version,
        project_root=project_root,
        files=files,
        git=git,
        dry_run=dry_run,
        config_version_updater=config_version_updater,
    )


def some_planned_change(
    file=Path(SOME_GLOB_MATCHED_FILE_NAME),
    line_index=SOME_FILE_INDEX,
    old_line=SOME_OLD_LINE,
    new_line=SOME_NEW_LINE,
) -> PlannedChange:
    return PlannedChange(
        file=file, line_index=line_index, old_line=old_line, new_line=new_line
    )


@dataclass
class InitedRepo:
    repo: Repo
    path: Path
    remote_repo: Repo
    committed_file: Path


def some_git_repo(
    test_root: Path,
    remote: Optional[str] = None,
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    detached: bool = False,
) -> InitedRepo:
    """
    Initialize test repository setup (a primary with a single commit and remote with no commits)

    :param test_root: Directory to store repositories.
    :param remote: Name to use when referencing remote repo. If `None` the remote repo will not be
        linked to the primary_repo.
    :param branch: Name to use for an additional branch created on the primary repository. If
        `None`, no branch will be created.
    :param tag: Name to use for a tag created on the primary repository. If `None`, no tag will be
        created.
    :param detached: If `True`, switch from the default branch to a detached HEAD situation that
        only points to the initial commit.
    :return: Data about the initialized repos.
    """
    repo_dir = test_root / "primary"
    repo = Repo.init(repo_dir, mkdir=True)
    remote_path = test_root / "other"
    remote_repo = Repo.init(test_root / "other", mkdir=True, bare=True)

    file = repo_dir / SOME_GLOB_MATCHED_FILE_NAME
    file.touch()
    repo.index.add([file])
    repo.index.commit("a first commit")

    if remote is not None:
        repo.create_remote(remote, str(remote_path))

    if branch is not None:
        repo.create_head(branch)

    if tag is not None:
        repo.create_tag(tag)

    if detached:
        repo.head.reference = repo.commit("HEAD")

    return InitedRepo(repo, repo_dir, remote_repo, file)
