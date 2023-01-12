from pathlib import Path

import tomlkit

from hyper_bump_it._hyper_bump_it import core
from hyper_bump_it._hyper_bump_it.config import (
    Config,
    ConfigVersionUpdater,
    GitAction,
    file,
)
from tests._hyper_bump_it import sample_data as sd


def test_do_bump__keystone_no_git_confirm_prompt__file_updated(
    tmp_path: Path, force_input
):
    force_input("y")
    config = sd.some_application_config(
        project_root=tmp_path,
        git=sd.some_git(
            actions=sd.some_git_actions(GitAction.Skip, GitAction.Skip, GitAction.Skip)
        ),
        config_version_updater=None,
    )
    _keystone_file_updated(tmp_path, config)


def test_do_bump__keystone_no_git_skip_confirm_prompt__file_updated(tmp_path: Path):
    config = sd.some_application_config(
        project_root=tmp_path,
        git=sd.some_git(
            actions=sd.some_git_actions(GitAction.Skip, GitAction.Skip, GitAction.Skip)
        ),
        show_confirm_prompt=False,
        config_version_updater=None,
    )
    _keystone_file_updated(tmp_path, config)


def _keystone_file_updated(tmp_path: Path, config: Config):
    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    some_file.write_text(original_text)

    core.do_bump(config)

    new_content = some_file.read_text()
    assert new_content == f"--{sd.SOME_OTHER_VERSION}--"


def test_do_bump__config_version_no_git__files_updated(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_text = sd.some_minimal_config_text(
        file.ROOT_TABLE_KEY, sd.SOME_VERSION_STRING
    )
    config_file.write_text(config_text)
    toml_doc = tomlkit.parse(config_text)
    config = sd.some_application_config(
        project_root=tmp_path,
        git=sd.some_git(
            actions=sd.some_git_actions(GitAction.Skip, GitAction.Skip, GitAction.Skip)
        ),
        show_confirm_prompt=False,
        config_version_updater=ConfigVersionUpdater(
            config_file, toml_doc, toml_doc[file.ROOT_TABLE_KEY]
        ),
    )

    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    some_file.write_text(original_text)

    core.do_bump(config)

    new_content = some_file.read_text()
    new_config_content = config_file.read_text()
    assert new_content == f"--{sd.SOME_OTHER_VERSION}--"
    assert new_config_content == sd.some_minimal_config_text(
        file.ROOT_TABLE_KEY, sd.SOME_OTHER_VERSION
    )


def test_do_bump__keystone_git__file_updated(tmp_path: Path):
    git_repo = sd.some_git_repo(tmp_path, remote=sd.SOME_REMOTE)
    project_root = git_repo.committed_file.parent
    config = sd.some_application_config(
        project_root=project_root,
        show_confirm_prompt=False,
        config_version_updater=None,
    )

    original_text = f"--{sd.SOME_VERSION}--"
    some_file = project_root / sd.SOME_GLOB_MATCHED_FILE_NAME
    some_file.write_text(original_text)
    git_repo.repo.index.add([some_file])
    git_repo.repo.index.commit("commit file to be updated")

    core.do_bump(config)

    new_content = some_file.read_text()
    assert new_content == f"--{sd.SOME_OTHER_VERSION}--"
    commit_diff = git_repo.repo.head.commit.diff("HEAD^")
    assert len(commit_diff) == 1
    assert (
        commit_diff[0].a_path == sd.SOME_GLOB_MATCHED_FILE_NAME
        and commit_diff[0].change_type == "M"
    )


def test_do_bump__keystone_no_git_decline_prompt__file_unchanged(
    tmp_path: Path, force_input
):
    force_input("n")
    config = sd.some_application_config(
        project_root=tmp_path,
        git=sd.some_git(
            actions=sd.some_git_actions(GitAction.Skip, GitAction.Skip, GitAction.Skip)
        ),
        config_version_updater=None,
    )
    _no_edits(tmp_path, config)


def test_do_bump__keystone_no_git_dry_run__file_unchanged(tmp_path: Path, force_input):
    config = sd.some_application_config(
        project_root=tmp_path,
        git=sd.some_git(
            actions=sd.some_git_actions(GitAction.Skip, GitAction.Skip, GitAction.Skip)
        ),
        config_version_updater=None,
        dry_run=True,
    )
    _no_edits(tmp_path, config)


def _no_edits(tmp_path: Path, config: Config):
    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    some_file.write_text(original_text)

    core.do_bump(config)

    new_content = some_file.read_text()
    assert new_content == original_text
