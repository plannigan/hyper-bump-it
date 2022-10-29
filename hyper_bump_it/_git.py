"""
Operation on git repositories.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from git import InvalidGitRepositoryError, Repo

from hyper_bump_it._config import GitAction, GitActions, GitConfig
from hyper_bump_it._error import (
    AlreadyExistsError,
    DetachedRepositoryError,
    DirtyRepositoryError,
    MissingRemoteError,
    NoRepositoryError,
)
from hyper_bump_it._text_formatter import TextFormatter


@dataclass
class GitOperationsInfo:
    remote: str
    commit_message: str
    branch_name: str
    tag_name: str
    actions: GitActions

    @classmethod
    def from_config(
        cls, config: GitConfig, formatter: TextFormatter
    ) -> "GitOperationsInfo":
        """
        Convert the configuration into the necessary operation information.

        :param config: Configuration of how git operations should operate.
        :param formatter: Object that converts format patterns into text.
        :return: Git operation information.
        :raises FormatError: Format pattern was invalid or attempted to use an invalid key.
        """
        return cls(
            remote=config.remote,
            commit_message=formatter.format(config.commit_format_pattern),
            branch_name=formatter.format(config.branch_format_pattern),
            tag_name=formatter.format(config.tag_format_pattern),
            actions=config.actions,
        )


def get_vetted_repo(project_root: Path, operation_info: GitOperationsInfo) -> Repo:
    """
    Retrieve the git repository, ensuring it is in the expected state.

    :param project_root: Root of the project repository.
    :param operation_info: Git operation information.
    :return: Repository that is valid for the planned operations.
    :raises GitError: Repository was not compatible with the configured git operations.
    """
    try:
        repo = Repo(project_root)
    except InvalidGitRepositoryError:
        raise NoRepositoryError(project_root)

    if repo.is_dirty():
        raise DirtyRepositoryError(repo)

    if repo.head.is_detached:
        raise DetachedRepositoryError(repo)

    if operation_info.actions.any_push and operation_info.remote not in repo.remotes:
        raise MissingRemoteError(operation_info.remote)

    if (
        operation_info.actions.branch.should_create
        and operation_info.branch_name in repo.heads
    ):
        raise AlreadyExistsError("branch", operation_info.branch_name)
    if (
        operation_info.actions.tag.should_create
        and operation_info.tag_name in repo.tags
    ):
        raise AlreadyExistsError("tag", operation_info.tag_name)

    return repo


@contextmanager
def switch_to_branch(repo: Repo, branch_name: str) -> Iterator[None]:
    initial_branch = repo.active_branch
    branch = repo.create_head(branch_name)
    branch.checkout()
    try:
        yield
    finally:
        initial_branch.checkout()


def commit_changes(repo: Repo, commit_message: str) -> None:
    index = repo.index
    for diff in index.diff(None):
        if diff.deleted_file:
            index.remove(diff.a_path)
        else:
            index.add(diff.a_path)
    for file in repo.untracked_files:
        index.add(file)

    index.commit(commit_message)


def create_tag(repo: Repo, tag_name: str) -> None:
    repo.create_tag(tag_name)


def push_changes(repo: Repo, operation_info: GitOperationsInfo) -> None:
    to_push = [
        operation_info.branch_name
        if operation_info.actions.branch == GitAction.CreateAndPush
        else repo.active_branch.name
    ]
    if operation_info.actions.tag == GitAction.CreateAndPush:
        to_push.append(operation_info.tag_name)

    remote = repo.remotes[operation_info.remote]
    remote.push(to_push, atomic=True)
