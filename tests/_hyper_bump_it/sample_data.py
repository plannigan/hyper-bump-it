"""
Common test data that can be used across multiple test cases.
"""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from textwrap import dedent
from typing import Optional, Union

from git import Repo
from tomlkit import TOMLDocument

from hyper_bump_it._hyper_bump_it.config import (
    BumpByArgs,
    BumpPart,
    BumpToArgs,
    Config,
    ConfigFile,
    File,
    FileDefinition,
    Git,
    GitAction,
    GitActions,
    GitActionsConfigFile,
    GitConfigFile,
)
from hyper_bump_it._hyper_bump_it.config.file import ConfigVersionUpdater
from hyper_bump_it._hyper_bump_it.files import LineChange, PlannedChange
from hyper_bump_it._hyper_bump_it.text_formatter import TextFormatter, keys
from hyper_bump_it._hyper_bump_it.vcs import GitOperationsInfo
from hyper_bump_it._hyper_bump_it.version import Version

ALL_KEYS = tuple(getattr(keys, name) for name in dir(keys) if not name.startswith("__"))

SOME_DATE = date(year=2022, month=10, day=19)
SOME_MAJOR = 1
SOME_MINOR = 2
SOME_PATCH = 3
SOME_PRERELEASE = "11.22"
SOME_PRERELEASE_PARTS = tuple(SOME_PRERELEASE.split("."))
SOME_BUILD = "b123.321"
SOME_BUILD_PARTS = tuple(SOME_BUILD.split("."))
SOME_VERSION = Version(
    major=SOME_MAJOR,
    minor=SOME_MINOR,
    patch=SOME_PATCH,
    prerelease=SOME_PRERELEASE_PARTS,
    build=SOME_BUILD_PARTS,
)
SOME_VERSION_STRING = str(SOME_VERSION)
SOME_OTHER_MAJOR = 4
SOME_OTHER_MINOR = 5
SOME_OTHER_PATCH = 6
SOME_OTHER_PRERELEASE = "33.44"
SOME_OTHER_PRERELEASE_PARTS = tuple(SOME_OTHER_PRERELEASE.split("."))
SOME_OTHER_BUILD = "b456.654"
SOME_OTHER_BUILD_PARTS = tuple(SOME_OTHER_BUILD.split("."))
SOME_OTHER_VERSION = Version(
    major=SOME_OTHER_MAJOR,
    minor=SOME_OTHER_MINOR,
    patch=SOME_OTHER_PATCH,
    prerelease=SOME_OTHER_PRERELEASE_PARTS,
    build=SOME_OTHER_BUILD_PARTS,
)
SOME_OTHER_VERSION_STRING = str(SOME_OTHER_VERSION)
SOME_OTHER_PARTIAL_VERSION = Version(
    major=SOME_OTHER_MAJOR,
    minor=SOME_OTHER_MINOR,
    patch=SOME_OTHER_PATCH,
)
SOME_OTHER_PARTIAL_VERSION_STRING = str(SOME_OTHER_PARTIAL_VERSION)
SOME_NON_VERSION_STRING = "abc-123"
SOME_BUMP_PART = BumpPart.Minor
SOME_CONFIG_FILE_NAME = "config.toml"
SOME_DIRECTORY_NAME = "test-dir"
SOME_ERROR_MESSAGE = "it went bang"


def some_text_formatter(
    current_version: Version = SOME_VERSION,
    new_version: Version = SOME_OTHER_VERSION,
    today: date = SOME_DATE,
) -> TextFormatter:
    return TextFormatter(current_version, new_version, today)


SOME_REMOTE = "test-remote"
SOME_OTHER_REMOTE = "other-test-remote"
SOME_COMMIT_MESSAGE = "test commit message"
SOME_OTHER_COMMIT_MESSAGE = "other test commit message"
SOME_BRANCH = "test-branch"
SOME_OTHER_BRANCH = "other-test-branch"
SOME_TAG = "test-tag"
SOME_OTHER_TAG = "other-test-tag"
SOME_COMMIT_PATTERN = f"test commit {{{keys.NEW_VERSION}}}"
SOME_OTHER_COMMIT_PATTERN = f"other test commit {{{keys.NEW_VERSION}}}"
SOME_BRANCH_PATTERN = f"test-branch-{{{keys.NEW_VERSION}}}"
SOME_OTHER_BRANCH_PATTERN = f"other test-branch-{{{keys.NEW_VERSION}}}"
SOME_TAG_PATTERN = f"test-tag-{{{keys.NEW_VERSION}}}"
SOME_OTHER_TAG_PATTERN = f"other-test-tag-{{{keys.NEW_VERSION}}}"

SOME_COMMIT_ACTION = GitAction.CreateAndPush
SOME_BRANCH_ACTION = GitAction.Skip
SOME_TAG_ACTION = GitAction.Create
SOME_NON_GIT_ACTION_STRING = "other"

SOME_FILE_INDEX = 3
SOME_OTHER_FILE_INDEX = 5
SOME_OLD_LINE = "start text"
SOME_OTHER_OLD_LINE = "other start text"
SOME_NEW_LINE = "updated text"
SOME_OTHER_NEW_LINE = "other updated text"


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


def some_git_actions_config_file(
    commit=SOME_COMMIT_ACTION,
    branch=SOME_BRANCH_ACTION,
    tag=SOME_TAG_ACTION,
) -> GitActionsConfigFile:
    return GitActionsConfigFile(commit=commit, branch=branch, tag=tag)


def some_git_config_file(
    remote=SOME_REMOTE,
    commit_format_pattern=SOME_COMMIT_PATTERN,
    branch_format_pattern=SOME_BRANCH_PATTERN,
    tag_format_pattern=SOME_TAG_PATTERN,
    actions=some_git_actions_config_file(),
) -> GitConfigFile:
    return GitConfigFile(
        remote=remote,
        commit_format_pattern=commit_format_pattern,
        branch_format_pattern=branch_format_pattern,
        tag_format_pattern=tag_format_pattern,
        actions=actions,
    )


SOME_PROJECT_ROOT = Path("fake-project-root-dir")
SOME_FILE_GLOB = "foo*.txt"
SOME_OTHER_FILE_GLOB = "bar*.txt"
SOME_GLOB_MATCHED_FILE_NAME = "foo-1.txt"
SOME_OTHER_GLOB_MATCHED_FILE_NAME = "foo-2.txt"
SOME_SEARCH_FORMAT_PATTERN = f"{{{keys.VERSION}}}"
SOME_OTHER_SEARCH_FORMAT_PATTERN = f"other {{{keys.VERSION}}}"
SOME_REPLACE_FORMAT_PATTERN = f"{{{keys.NEW_VERSION}}}"
SOME_OTHER_REPLACE_FORMAT_PATTERN = f"other {{{keys.NEW_VERSION}}}"
SOME_INVALID_FORMAT_PATTERN = "invalid  --{-- pattern"


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


def some_file_definition(
    file_glob=SOME_FILE_GLOB,
    keystone: bool = False,
    search_format_pattern=SOME_SEARCH_FORMAT_PATTERN,
    replace_format_pattern=SOME_REPLACE_FORMAT_PATTERN,
) -> FileDefinition:
    return FileDefinition(
        file_glob=file_glob,
        keystone=keystone,
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


SOME_SHOW_CONFIRM_PROMPT = True
SOME_PYPROJECT = False


def some_config_file(
    current_version: Optional[Version] = SOME_VERSION,
    show_confirm_prompt: bool = SOME_SHOW_CONFIRM_PROMPT,
    files: Union[list[FileDefinition], FileDefinition] = some_file_definition(),
    git: GitConfigFile = some_git_config_file(),
) -> ConfigFile:
    if isinstance(files, FileDefinition):
        files = [files]

    return ConfigFile(
        current_version=current_version,
        show_confirm_prompt=show_confirm_prompt,
        files=files,
        git=git,
    )


def some_minimal_config_text(
    table_root: str,
    version: Optional[str],
    file_glob: Optional[str] = SOME_FILE_GLOB,
    show_confirm_prompt: Optional[bool] = None,
    trim_empty_lines: bool = False,
    include_empty_tables: bool = True,
) -> str:
    root_table_header = f"[{table_root}]"
    if version is None:
        current_version = ""
        keystone = "keystone = true"
    else:
        current_version = f'current_version = "{version}"'
        keystone = ""
    show_confirm_prompt_text = (
        ""
        if show_confirm_prompt is None
        else f"show_confirm_prompt = {str(show_confirm_prompt).lower()}"
    )
    if not include_empty_tables and version is None and show_confirm_prompt is None:
        root_table_header = ""
    content = dedent(
        f"""\
        {root_table_header}
        {current_version}
        {show_confirm_prompt_text}
        [[{table_root}.files]]
        file_glob = "{file_glob}"
        {keystone}
"""
    )
    if trim_empty_lines:
        content = "\n".join(line for line in content.splitlines() if line != "") + "\n"
    return content


def no_config_override_bump_to_args(
    project_root: Path,
    new_version: Version = SOME_OTHER_VERSION,
    config_file: Optional[Path] = None,
    dry_run: bool = False,
    skip_confirm_prompt: Optional[bool] = None,
) -> BumpToArgs:
    return BumpToArgs(
        new_version=new_version,
        config_file=config_file,
        project_root=project_root,
        dry_run=dry_run,
        skip_confirm_prompt=skip_confirm_prompt,
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
    skip_confirm_prompt: Optional[bool] = None,
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
        skip_confirm_prompt=skip_confirm_prompt,
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
    skip_confirm_prompt: Optional[bool] = None,
) -> BumpByArgs:
    return BumpByArgs(
        part_to_bump=part_to_bump,
        config_file=config_file,
        project_root=project_root,
        dry_run=dry_run,
        skip_confirm_prompt=skip_confirm_prompt,
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
    skip_confirm_prompt: Optional[bool] = None,
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
        skip_confirm_prompt=skip_confirm_prompt,
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
    show_confirm_prompt: bool = True,
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
        show_confirm_prompt=show_confirm_prompt,
        config_version_updater=config_version_updater,
    )


def some_line_change(
    line_index=SOME_FILE_INDEX,
    old_line=SOME_OLD_LINE,
    new_line=SOME_NEW_LINE,
) -> LineChange:
    return LineChange(line_index=line_index, old_line=old_line, new_line=new_line)


def some_planned_change(
    file=Path(SOME_GLOB_MATCHED_FILE_NAME),
    line_changes: Union[LineChange, list[LineChange]] = some_line_change(),
) -> PlannedChange:
    if not isinstance(line_changes, list):
        line_changes = [line_changes]
    return PlannedChange(file=file, line_changes=line_changes)


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
