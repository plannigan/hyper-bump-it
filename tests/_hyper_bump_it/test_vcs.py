from pathlib import Path

import pytest
from git import Repo

from hyper_bump_it._hyper_bump_it import vcs
from hyper_bump_it._hyper_bump_it.config import GitAction, GitActions
from hyper_bump_it._hyper_bump_it.error import (
    AlreadyExistsError,
    DetachedRepositoryError,
    DirtyRepositoryError,
    DisallowedInitialBranchError,
    EmptyRepositoryError,
    MissingRemoteError,
    NoRepositoryError,
)
from hyper_bump_it._hyper_bump_it.vcs import GitOperationsInfo
from tests._hyper_bump_it import sample_data as sd

TEXT_FORMATTER = sd.some_text_formatter()
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
        tag_message=TEXT_FORMATTER.format(sd.SOME_TAG_MESSAGE_PATTERN),
        allowed_initial_branches=sd.SOME_ALLOWED_BRANCHES,
        actions=git_actions,
    )


def test_get_vetted_repo__not_repo__error(tmp_path: Path):
    with pytest.raises(NoRepositoryError):
        vcs.get_vetted_repo(tmp_path, sd.some_git_operations_info())


def test_get_vetted_repo__dirty_repo__error(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)
    repo.committed_file.write_text("SOME NEW TEXT")
    repo.repo.index.add([repo.committed_file])

    with pytest.raises(DirtyRepositoryError):
        vcs.get_vetted_repo(repo.path, sd.some_git_operations_info())


def test_get_vetted_repo__detached_head__error(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, detached=True)

    with pytest.raises(DetachedRepositoryError):
        vcs.get_vetted_repo(repo.path, sd.some_git_operations_info())


def test_get_vetted_repo__disallowed_branch__error(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, remote=None)

    with pytest.raises(DisallowedInitialBranchError):
        vcs.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                allowed_initial_branches=sd.SOME_ALLOWED_BRANCHES
            ),
        )


def test_get_vetted_repo__no_remote__error(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, remote=None)

    with pytest.raises(MissingRemoteError):
        vcs.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
                actions=sd.some_git_actions(commit=GitAction.CreateAndPush),
            ),
        )


def test_get_vetted_repo__existing_branch__error(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, branch=sd.SOME_BRANCH)

    with pytest.raises(AlreadyExistsError, match="branch"):
        vcs.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
                actions=sd.some_git_actions(
                    commit=GitAction.Create,
                    branch=GitAction.Create,
                ),
            ),
        )


def test_get_vetted_repo__no_commits_create_branch_plan__error(tmp_path: Path):
    repo = Repo.init(tmp_path)
    print(repo.heads)

    with pytest.raises(EmptyRepositoryError):
        vcs.get_vetted_repo(
            tmp_path,
            sd.some_git_operations_info(
                allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
                actions=sd.some_git_actions(
                    commit=GitAction.Create, branch=GitAction.Create
                ),
            ),
        )


def test_get_vetted_repo__existing_branch_no_branching__repo_returned(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, branch=sd.SOME_BRANCH)

    result = vcs.get_vetted_repo(
        repo.path,
        sd.some_git_operations_info(
            allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
            actions=sd.some_git_actions(commit=GitAction.Create, branch=GitAction.Skip),
        ),
    )

    assert result == repo.repo


def test_get_vetted_repo__existing_tag__error(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, tag=sd.SOME_TAG)

    with pytest.raises(AlreadyExistsError, match="tag"):
        vcs.get_vetted_repo(
            repo.path,
            sd.some_git_operations_info(
                allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
                actions=sd.some_git_actions(
                    commit=GitAction.Create,
                    branch=GitAction.Skip,
                    tag=GitAction.Create,
                ),
            ),
        )


def test_get_vetted_repo__existing_tag_no_tagging__repo_returned(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, tag=sd.SOME_TAG)

    result = vcs.get_vetted_repo(
        repo.path,
        sd.some_git_operations_info(
            allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
            actions=GitActions(
                commit=GitAction.Skip,
                branch=GitAction.Skip,
                tag=GitAction.Skip,
            ),
        ),
    )
    assert result == repo.repo


def test_create_branch__result_has_name(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)

    vcs.create_branch(repo.repo, sd.SOME_BRANCH)

    assert sd.SOME_BRANCH in repo.repo.heads


def test_switch_to__active_branch_is_expected(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, branch=sd.SOME_BRANCH)

    vcs.switch_to(repo.repo, sd.SOME_BRANCH)

    assert repo.repo.active_branch.name == sd.SOME_BRANCH


def test_commit_change__edited_file__in_commit(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)
    repo.committed_file.write_text("SOME NEW TEXT")

    vcs.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit_diff = repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 1
    assert (
        commit_diff[0].a_path == sd.SOME_GLOB_MATCHED_FILE_NAME
        and commit_diff[0].change_type == "M"
    )


def test_commit_change__edited_file__message_from_pattern(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)
    repo.committed_file.write_text("SOME NEW TEXT")

    vcs.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit = repo.repo.head.commit
    assert commit.message == sd.SOME_COMMIT_MESSAGE


def test_commit_change__deleted_file__in_commit(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)
    repo.committed_file.unlink()

    vcs.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit_diff = repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 1
    assert (
        commit_diff[0].a_path == sd.SOME_GLOB_MATCHED_FILE_NAME
        and commit_diff[0].new_file
    )


def test_commit_change__new_file__not_in_commit(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)
    repo.path.joinpath(SOME_OTHER_FILE).write_text("")

    vcs.commit_changes(repo.repo, sd.SOME_COMMIT_MESSAGE)

    commit_diff = repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 0


def test_create_tag__repo_tagged_head_commit(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)

    vcs.create_tag(repo.repo, sd.SOME_TAG, sd.SOME_TAG_MESSAGE)

    assert sd.SOME_TAG in repo.repo.tags
    assert repo.repo.tags[sd.SOME_TAG].commit == repo.repo.active_branch.commit


def test_create_tag__tag_contains_message(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)

    vcs.create_tag(repo.repo, sd.SOME_TAG, sd.SOME_TAG_MESSAGE)

    assert sd.SOME_TAG in repo.repo.tags
    assert sd.SOME_TAG_MESSAGE in repo.repo.tags[sd.SOME_TAG].tag.message


def test_push_changes__no_branch_no_tag__only_commit_pushed(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, remote=sd.SOME_REMOTE)

    vcs.push_changes(
        repo.repo,
        sd.some_git_operations_info(
            actions=sd.some_git_actions(branch=GitAction.Skip, tag=GitAction.Skip),
        ),
    )

    assert repo.remote_repo.active_branch.commit == repo.repo.active_branch.commit
    assert sd.SOME_BRANCH not in repo.remote_repo.heads
    assert sd.SOME_TAG not in repo.remote_repo.tags


def test_push_changes__tag_no_push__commit_pushed_but_not_tag(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, remote=sd.SOME_REMOTE)
    repo.repo.create_tag(sd.SOME_TAG, message=sd.SOME_TAG_MESSAGE)

    vcs.push_changes(
        repo.repo,
        sd.some_git_operations_info(
            actions=sd.some_git_actions(branch=GitAction.Skip, tag=GitAction.Create),
        ),
    )

    assert repo.remote_repo.active_branch.commit == repo.repo.active_branch.commit
    assert sd.SOME_TAG not in repo.remote_repo.tags


def test_push_changes__tag_and_push__commit_and_tag_pushed(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path, remote=sd.SOME_REMOTE)
    repo.repo.create_tag(sd.SOME_TAG, message=sd.SOME_TAG_MESSAGE)

    vcs.push_changes(
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


def test_get_vetted_repo__on_allowed_branch__valid(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)

    result = vcs.get_vetted_repo(
        repo.path,
        sd.some_git_operations_info(
            allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
            actions=sd.some_git_actions(
                commit=GitAction.Create, branch=GitAction.Skip, tag=GitAction.Skip
            ),
        ),
    )
    assert result == repo.repo


def test_get_vetted_repo__no_disallowed_branches__valid(tmp_path: Path):
    repo = sd.some_git_repo(tmp_path)

    result = vcs.get_vetted_repo(
        repo.path,
        sd.some_git_operations_info(
            allowed_initial_branches=sd.ANY_ALLOWED_BRANCHES,
            actions=sd.some_git_actions(
                commit=GitAction.Create, branch=GitAction.Skip, tag=GitAction.Skip
            ),
        ),
    )
    assert result == repo.repo


class FakeException(Exception):
    pass
