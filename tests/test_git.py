from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest
from git import Repo

from hyper_bump_it import _git as git
from hyper_bump_it._config import GitAction, GitActions
from hyper_bump_it._error import (
    AlreadyExistsError,
    DetachedRepositoryError,
    DirtyRepositoryError,
    MissingRemoteError,
    NoRepositoryError,
)
from hyper_bump_it._git import GitOperationsInfo
from tests import sample_data as sd

TEXT_FORMATTER = sd.some_text_formatter()
SOME_FILE = "foo.txt"
SOME_OTHER_FILE = "bar.txt"


def test_from_config__names_formatted_from_pattern():
    git_actions = sd.some_git_actions()
    initial_config = sd.some_git(actions=git_actions)

    operations_info = GitOperationsInfo.from_config(initial_config, TEXT_FORMATTER)

    assert operations_info == GitOperationsInfo(
        remote=sd.SOME_REMOTE,
        commit_message=TEXT_FORMATTER.format(sd.SOME_COMMIT_PATTERN),
        branch_name=TEXT_FORMATTER.format(sd.SOME_BRANCH_PATTERN),
        tag_name=TEXT_FORMATTER.format(sd.SOME_TAG_PATTERN),
        actions=git_actions,
    )


def test_get_vetted_repo__not_repo__error(tmp_path: Path):
    with pytest.raises(NoRepositoryError):
        git.get_vetted_repo(tmp_path, sd.some_git_operations_info())


def test_get_vetted_repo__dirty_repo__error(tmp_path: Path):
    repo = _init_repo(tmp_path)
    repo.committed_file.write_text("SOME NEW TEXT")
    repo.repo.index.add([repo.committed_file])

    with pytest.raises(DirtyRepositoryError):
        git.get_vetted_repo(repo.path, sd.some_git_operations_info())


def test_get_vetted_repo__detached_head__error(tmp_path: Path):
    repo = _init_repo(tmp_path, detached=True)

    with pytest.raises(DetachedRepositoryError):
        git.get_vetted_repo(repo.path, sd.some_git_operations_info())


def test_get_vetted_repo__no_remote__error(tmp_path: Path):
    repo = _init_repo(tmp_path, remote=None)

    with pytest.raises(MissingRemoteError):
        git.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                actions=sd.some_git_actions(commit=GitAction.CreateAndPush)
            ),
        )


def test_get_vetted_repo__existing_branch__error(tmp_path: Path):
    repo = _init_repo(tmp_path, branch=sd.SOME_BRANCH)

    with pytest.raises(AlreadyExistsError, match="branch"):
        git.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                actions=sd.some_git_actions(branch=GitAction.Create)
            ),
        )


def test_get_vetted_repo__existing_branch_no_branching__repo_returned(tmp_path: Path):
    repo = _init_repo(tmp_path, branch=sd.SOME_BRANCH)

    result = git.get_vetted_repo(
        repo.path,
        sd.some_git_operations_info(actions=sd.some_git_actions(branch=GitAction.Skip)),
    )

    assert result == repo.repo


def test_get_vetted_repo__existing_tag__error(tmp_path: Path):
    repo = _init_repo(tmp_path, tag=sd.SOME_TAG)

    with pytest.raises(AlreadyExistsError, match="tag"):
        git.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                actions=sd.some_git_actions(
                    commit=GitAction.Create,
                    branch=GitAction.Skip,
                    tag=GitAction.Create,
                )
            ),
        )


def test_get_vetted_repo__existing_tag_no_tagging__repo_returned(tmp_path: Path):
    repo = _init_repo(tmp_path, tag=sd.SOME_TAG)

    result = git.get_vetted_repo(
        repo.path,
        sd.some_git_operations_info(
            actions=GitActions(
                commit=GitAction.Skip,
                branch=GitAction.Skip,
                tag=GitAction.Skip,
            ),
        ),
    )
    assert result == repo.repo


def test_switch_to_branch__on_branch_in_context(tmp_path: Path):
    repo = _init_repo(tmp_path)

    with git.switch_to_branch(repo.repo, sd.SOME_BRANCH):
        assert repo.repo.active_branch.name == sd.SOME_BRANCH


def test_switch_to_branch__back_to_initial_branch_after_context(tmp_path: Path):
    repo = _init_repo(tmp_path)

    initial_branch = repo.repo.active_branch
    with git.switch_to_branch(repo.repo, sd.some_git_operations_info().branch_name):
        pass

    assert repo.repo.active_branch == initial_branch


def test_switch_to_branch__exception__back_to_initial_branch_after_context(
    tmp_path: Path,
):
    repo = _init_repo(tmp_path)

    initial_branch = repo.repo.active_branch
    try:
        with git.switch_to_branch(repo.repo, sd.some_git_operations_info().branch_name):
            raise FakeException("A test exception")
    except FakeException:
        pass

    assert repo.repo.active_branch == initial_branch


def test_commit_change__edited_file__in_commit(tmp_path: Path):
    repo = _init_repo(tmp_path)
    repo.committed_file.write_text("SOME NEW TEXT")

    git.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit_diff = repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 1
    assert commit_diff[0].a_path == SOME_FILE and commit_diff[0].change_type == "M"


def test_commit_change__edited_file__message_from_pattern(tmp_path: Path):
    repo = _init_repo(tmp_path)
    repo.committed_file.write_text("SOME NEW TEXT")

    git.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit = repo.repo.head.commit
    assert commit.message == sd.SOME_COMMIT_MESSAGE


def test_commit_change__deleted_file__in_commit(tmp_path: Path):
    repo = _init_repo(tmp_path)
    repo.committed_file.unlink()

    git.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit_diff = repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 1
    assert commit_diff[0].a_path == SOME_FILE and commit_diff[0].new_file


def test_commit_change__new_file__in_commit(tmp_path: Path):
    repo = _init_repo(tmp_path)
    repo.path.joinpath(SOME_OTHER_FILE).write_text("")

    git.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit_diff = repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 1
    assert commit_diff[0].a_path == SOME_OTHER_FILE and commit_diff[0].deleted_file


def test_create_tag__repo_tagged_head_commit(tmp_path: Path):
    repo = _init_repo(tmp_path)

    git.create_tag(repo.repo, sd.SOME_TAG)

    assert sd.SOME_TAG in repo.repo.tags
    assert repo.repo.tags[sd.SOME_TAG].commit == repo.repo.active_branch.commit


def test_push_changes__no_branch_no_tag__only_commit_pushed(tmp_path: Path):
    repo = _init_repo(tmp_path, remote=sd.SOME_REMOTE)

    git.push_changes(
        repo.repo,
        sd.some_git_operations_info(
            actions=sd.some_git_actions(branch=GitAction.Skip, tag=GitAction.Skip),
        ),
    )

    assert repo.remote_repo.active_branch.commit == repo.repo.active_branch.commit
    assert sd.SOME_BRANCH not in repo.remote_repo.heads
    assert sd.SOME_TAG not in repo.remote_repo.tags


def test_push_changes__tag_no_push__commit_pushed_but_not_tag(tmp_path: Path):
    repo = _init_repo(tmp_path, remote=sd.SOME_REMOTE)
    repo.repo.create_tag(sd.SOME_TAG)

    git.push_changes(
        repo.repo,
        sd.some_git_operations_info(
            actions=sd.some_git_actions(branch=GitAction.Skip, tag=GitAction.Create),
        ),
    )

    assert repo.remote_repo.active_branch.commit == repo.repo.active_branch.commit
    assert sd.SOME_TAG not in repo.remote_repo.tags


def test_push_changes__tag_and_push__commit_and_tag_pushed(tmp_path: Path):
    repo = _init_repo(tmp_path, remote=sd.SOME_REMOTE)
    repo.repo.create_tag(sd.SOME_TAG)

    git.push_changes(
        repo.repo,
        sd.some_git_operations_info(
            actions=sd.some_git_actions(
                branch=GitAction.Skip, tag=GitAction.CreateAndPush
            ),
        ),
    )

    assert repo.remote_repo.active_branch.commit == repo.repo.active_branch.commit
    assert sd.SOME_TAG in repo.remote_repo.tags
    assert repo.repo.tags[sd.SOME_TAG].commit == repo.repo.active_branch.commit


@dataclass
class InitedRepo:
    repo: Repo
    path: Path
    remote_repo: Repo
    committed_file: Path


def _init_repo(
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

    file = repo_dir / SOME_FILE
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


class FakeException(Exception):
    pass
