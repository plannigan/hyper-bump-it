from pathlib import Path
from textwrap import dedent

import pytest
from tomlkit import TOMLDocument

from hyper_bump_it._config import application, file
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


def test_config_from_file__explicit_version__expected_result(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=sd.SOME_VERSION)
    )

    config = application.config_from_file(sd.SOME_OTHER_VERSION, config_file, tmp_path)

    assert config == application.Config(
        current_version=sd.SOME_VERSION,
        new_version=sd.SOME_OTHER_VERSION,
        project_root=tmp_path,
        files=[
            application.File(
                file_glob=sd.SOME_FILE_GLOB,
                search_format_pattern=DEFAULT_SEARCH_PATTERN,
                replace_format_pattern=DEFAULT_SEARCH_PATTERN,
            )
        ],
        git=application.Git(
            remote=DEFAULT_REMOTE,
            commit_format_pattern=DEFAULT_COMMIT_FORMAT_PATTERN,
            branch_format_pattern=DEFAULT_BRANCH_FORMAT_PATTERN,
            tag_format_pattern=DEFAULT_TAG_FORMAT_PATTERN,
            actions=application.GitActions(
                commit=DEFAULT_COMMIT_ACTION,
                branch=DEFAULT_BRANCH_ACTION,
                tag=DEFAULT_TAG_ACTION,
            ),
        ),
        config_version_updater=AnyConfigVersionUpdater(),
    )


def test_config_from_file__keystone_version__expected_result(tmp_path: Path):
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

    config = application.config_from_file(sd.SOME_OTHER_VERSION, config_file, tmp_path)

    assert config == application.Config(
        current_version=sd.SOME_VERSION,
        new_version=sd.SOME_OTHER_VERSION,
        project_root=tmp_path,
        files=[
            application.File(
                file_glob=sd.SOME_FILE_GLOB,
                search_format_pattern=DEFAULT_SEARCH_PATTERN,
                replace_format_pattern=DEFAULT_SEARCH_PATTERN,
            )
        ],
        git=application.Git(
            remote=DEFAULT_REMOTE,
            commit_format_pattern=DEFAULT_COMMIT_FORMAT_PATTERN,
            branch_format_pattern=DEFAULT_BRANCH_FORMAT_PATTERN,
            tag_format_pattern=DEFAULT_TAG_FORMAT_PATTERN,
            actions=application.GitActions(
                commit=DEFAULT_COMMIT_ACTION,
                branch=DEFAULT_BRANCH_ACTION,
                tag=DEFAULT_TAG_ACTION,
            ),
        ),
        config_version_updater=None,
    )


def test_config_from_file__keystone_glob_no_match__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, version=None)
    )

    with pytest.raises(KeystoneFileGlobError):
        application.config_from_file(sd.SOME_OTHER_VERSION, config_file, tmp_path)


class AnyConfigVersionUpdater(file.ConfigVersionUpdater):
    """A helper object that compares equal to any ConfigVersionUpdater instance."""

    def __init__(self):
        super().__init__(Path(), TOMLDocument(), TOMLDocument())

    def __eq__(self, other):
        return isinstance(other, file.ConfigVersionUpdater)

    def __ne__(self, other):
        return not isinstance(other, file.ConfigVersionUpdater)

    def __repr__(self):
        return "<AnyConfigVersionUpdater>"
