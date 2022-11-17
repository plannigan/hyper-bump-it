"""
Common test data that can be used across multiple test cases.
"""
from datetime import date
from textwrap import dedent
from typing import Optional

from semantic_version import Version

from hyper_bump_it._config import File, Git, GitAction, GitActions
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
SOME_CONFIG_FILE_NAME = "config.toml"


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


def some_git_actions(
    commit=GitAction.Create,
    branch=GitAction.Create,
    tag=GitAction.Create,
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
