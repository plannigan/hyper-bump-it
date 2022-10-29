from pathlib import Path
from textwrap import dedent

import pytest

from hyper_bump_it._config import BumpPart, GitAction, application, file
from hyper_bump_it._config.core import (
    DEFAULT_BRANCH_ACTION,
    DEFAULT_BRANCH_FORMAT_PATTERN,
    DEFAULT_COMMIT_ACTION,
    DEFAULT_COMMIT_FORMAT_PATTERN,
    DEFAULT_REMOTE,
    DEFAULT_SEARCH_PATTERN,
    DEFAULT_TAG_ACTION,
    DEFAULT_TAG_FORMAT_PATTERN,
)
from hyper_bump_it._error import KeystoneFileGlobError
from tests import sample_data as sd
from tests.git_action_combinations import INVALID_COMBINATIONS, GitActionCombination


@pytest.mark.parametrize(["invalid_combination", "match"], INVALID_COMBINATIONS)
def test_git_actions__invalid_combination__error(
    invalid_combination: GitActionCombination, match: str
):
    with pytest.raises(ValueError, match=match):
        application.GitActions(**invalid_combination)


@pytest.mark.parametrize(
    ["combination", "expected"],
    [
        (
            {
                "commit": GitAction.CreateAndPush,
                "branch": GitAction.CreateAndPush,
                "tag": GitAction.CreateAndPush,
            },
            True,
        ),
        (
            {
                "commit": GitAction.Skip,
                "branch": GitAction.Skip,
                "tag": GitAction.Skip,
            },
            False,
        ),
        (
            {
                "commit": GitAction.CreateAndPush,
                "branch": GitAction.Skip,
                "tag": GitAction.Skip,
            },
            True,
        ),
        (
            {
                "commit": GitAction.CreateAndPush,
                "branch": GitAction.CreateAndPush,
                "tag": GitAction.Skip,
            },
            True,
        ),
        (
            {
                "commit": GitAction.CreateAndPush,
                "branch": GitAction.Skip,
                "tag": GitAction.CreateAndPush,
            },
            True,
        ),
    ],
)
def test_git_actions__any_push__expected_result(
    combination: GitActionCombination, expected: bool
):
    assert application.GitActions(**combination).any_push == expected


@pytest.mark.parametrize(
    ["combination", "expected"],
    [
        (
            {
                "commit": GitAction.Skip,
                "branch": GitAction.Skip,
                "tag": GitAction.Skip,
            },
            True,
        ),
        (
            {
                "commit": GitAction.Create,
                "branch": GitAction.Skip,
                "tag": GitAction.Skip,
            },
            False,
        ),
        (
            {
                "commit": GitAction.Create,
                "branch": GitAction.Create,
                "tag": GitAction.Skip,
            },
            False,
        ),
        (
            {
                "commit": GitAction.Create,
                "branch": GitAction.Create,
                "tag": GitAction.Skip,
            },
            False,
        ),
    ],
)
def test_git_actions__any_skip__expected_result(
    combination: GitActionCombination, expected: bool
):
    assert application.GitActions(**combination).all_skip == expected


def test_config_for_bump_to__explicit_config_file_version__expected_result(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=sd.SOME_VERSION)
    )

    config = application.config_for_bump_to(
        sd.no_config_override_bump_to_args(
            config_file=config_file, project_root=tmp_path
        )
    )

    assert config == sd.some_application_config(
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        git=_default_git(),
        project_root=tmp_path,
    )


def test_config_for_bump_to__keystone_version__expected_result(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )
    keystone_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    keystone_file.write_text(
        dedent(
            f"""\
    version: {sd.SOME_VERSION_STRING}
    """
        )
    )

    config = application.config_for_bump_to(
        sd.no_config_override_bump_to_args(
            config_file=config_file, project_root=tmp_path
        )
    )

    assert config == sd.some_application_config(
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        git=_default_git(),
        project_root=tmp_path,
        config_version_updater=None,
    )


def test_config_for_bump_to__cli_overrides__values_from_cli_not_config_fie(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )
    keystone_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    keystone_file.write_text(
        dedent(
            f"""\
    version: {sd.SOME_VERSION_STRING}
    """
        )
    )

    config = application.config_for_bump_to(
        sd.some_bump_to_args(config_file=config_file, project_root=tmp_path)
    )

    assert config == sd.some_application_config(
        current_version=sd.SOME_OTHER_PARTIAL_VERSION,
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        project_root=tmp_path,
        config_version_updater=None,
    )


def test_config_for_bump_to__cli_dry_run__values_has_dry_run(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=sd.SOME_VERSION)
    )

    config = application.config_for_bump_to(
        sd.no_config_override_bump_to_args(
            config_file=config_file, project_root=tmp_path, dry_run=True
        )
    )

    assert config == sd.some_application_config(
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        git=_default_git(),
        project_root=tmp_path,
        dry_run=True,
    )


def test_config_for_bump_to__keystone_glob_no_match__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )

    with pytest.raises(KeystoneFileGlobError, match="No files matched"):
        application.config_for_bump_to(
            sd.no_config_override_bump_to_args(
                config_file=config_file, project_root=tmp_path
            )
        )


def test_config_for_bump_to__keystone_glob_multi_match__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )
    for keystone_file_name in (
        sd.SOME_GLOB_MATCHED_FILE_NAME,
        sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME,
    ):
        keystone_file = tmp_path / keystone_file_name
        keystone_file.write_text(
            dedent(
                f"""\
        version: {sd.SOME_VERSION_STRING}
        """
            )
        )

    with pytest.raises(KeystoneFileGlobError, match="Matched: "):
        application.config_for_bump_to(
            sd.no_config_override_bump_to_args(
                config_file=config_file, project_root=tmp_path
            )
        )


def test_config_for_bump_by__explicit_config_file_version__expected_result(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=sd.SOME_VERSION)
    )

    config = application.config_for_bump_by(
        sd.no_config_override_bump_by_args(
            part_to_bump=BumpPart.Minor, config_file=config_file, project_root=tmp_path
        )
    )

    assert config == sd.some_application_config(
        new_version=sd.SOME_VERSION.next_minor(),
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        git=_default_git(),
        project_root=tmp_path,
    )


def test_config_for_bump_by__keystone_version__expected_result(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )
    keystone_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    keystone_file.write_text(
        dedent(
            f"""\
    version: {sd.SOME_VERSION_STRING}
    """
        )
    )

    config = application.config_for_bump_by(
        sd.no_config_override_bump_by_args(
            part_to_bump=BumpPart.Minor, config_file=config_file, project_root=tmp_path
        )
    )

    assert config == sd.some_application_config(
        new_version=sd.SOME_VERSION.next_minor(),
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        git=_default_git(),
        project_root=tmp_path,
        config_version_updater=None,
    )


def test_config_for_bump_by__cli_overrides__values_from_cli_not_config_fie(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )
    keystone_file = tmp_path / sd.SOME_GLOB_MATCHED_FILE_NAME
    keystone_file.write_text(
        dedent(
            f"""\
    version: {sd.SOME_VERSION_STRING}
    """
        )
    )

    config = application.config_for_bump_by(
        sd.some_bump_by_args(config_file=config_file, project_root=tmp_path)
    )

    assert config == sd.some_application_config(
        new_version=sd.SOME_OTHER_PARTIAL_VERSION.next_minor(),
        current_version=sd.SOME_OTHER_PARTIAL_VERSION,
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        project_root=tmp_path,
        config_version_updater=None,
    )


def test_config_for_bump_by__cli_dry_run__values_has_dry_run(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=sd.SOME_VERSION)
    )

    config = application.config_for_bump_by(
        sd.no_config_override_bump_by_args(
            part_to_bump=BumpPart.Minor,
            config_file=config_file,
            project_root=tmp_path,
            dry_run=True,
        )
    )

    assert config == sd.some_application_config(
        new_version=sd.SOME_VERSION.next_minor(),
        files=[_default_file(file_glob=sd.SOME_FILE_GLOB)],
        git=_default_git(),
        project_root=tmp_path,
        dry_run=True,
    )


def test_config_for_bump_by__keystone_glob_no_match__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )

    with pytest.raises(KeystoneFileGlobError, match="No files matched"):
        application.config_for_bump_by(
            sd.no_config_override_bump_by_args(
                config_file=config_file, project_root=tmp_path
            )
        )


def test_config_for_bump_by__keystone_glob_multi_match__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )
    for keystone_file_name in (
        sd.SOME_GLOB_MATCHED_FILE_NAME,
        sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME,
    ):
        keystone_file = tmp_path / keystone_file_name
        keystone_file.write_text(
            dedent(
                f"""\
        version: {sd.SOME_VERSION_STRING}
        """
            )
        )

    with pytest.raises(KeystoneFileGlobError, match="Matched: "):
        application.config_for_bump_by(
            sd.no_config_override_bump_by_args(
                config_file=config_file, project_root=tmp_path
            )
        )


def _default_file(file_glob: str) -> application.File:
    return application.File(
        file_glob=file_glob,
        search_format_pattern=DEFAULT_SEARCH_PATTERN,
        replace_format_pattern=DEFAULT_SEARCH_PATTERN,
    )


def _default_git() -> application.Git:
    return application.Git(
        remote=DEFAULT_REMOTE,
        commit_format_pattern=DEFAULT_COMMIT_FORMAT_PATTERN,
        branch_format_pattern=DEFAULT_BRANCH_FORMAT_PATTERN,
        tag_format_pattern=DEFAULT_TAG_FORMAT_PATTERN,
        actions=application.GitActions(
            commit=DEFAULT_COMMIT_ACTION,
            branch=DEFAULT_BRANCH_ACTION,
            tag=DEFAULT_TAG_ACTION,
        ),
    )
