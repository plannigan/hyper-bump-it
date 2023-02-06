from pathlib import Path

import pytest

from hyper_bump_it._hyper_bump_it.cli.interactive.file_validation import (
    DefinitionValidator,
    FailureType,
)
from hyper_bump_it._hyper_bump_it.text_formatter import FormatContext
from tests._hyper_bump_it import sample_data as sd


def test_validation__no_matched_files__failure(tmp_path: Path):
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=tmp_path)
    definition = sd.some_file_definition()

    result = validator(definition)

    assert result.failure_type == FailureType.NoFiles
    assert definition.file_glob in result.description
    assert str(tmp_path) in result.description


def test_validation__keystone_multiple_matched_files__failure(tmp_path: Path):
    tmp_path.joinpath(sd.SOME_GLOB_MATCHED_FILE_NAME).touch()
    tmp_path.joinpath(sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME).touch()
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=tmp_path)
    definition = sd.some_file_definition(keystone=True)

    result = validator(definition)

    assert result.failure_type == FailureType.KeystoneMultipleFiles
    assert definition.file_glob in result.description
    assert (
        sd.SOME_GLOB_MATCHED_FILE_NAME in result.description
        and sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME in result.description
    )


def test_validation__keystone_multiple_matched_files__paths_relative_to_root(
    tmp_path: Path,
):
    tmp_path.joinpath(sd.SOME_GLOB_MATCHED_FILE_NAME).touch()
    tmp_path.joinpath(sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME).touch()
    resolved_root = tmp_path.resolve()
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=resolved_root)
    definition = sd.some_file_definition(keystone=True)

    result = validator(definition)

    assert result.failure_type == FailureType.KeystoneMultipleFiles
    assert definition.file_glob in result.description
    assert str(resolved_root) not in result.description


@pytest.mark.parametrize(
    ["pattern_name", "expected_failure_type"],
    [
        ("search_format_pattern", FailureType.BadSearchPattern),
        ("replace_format_pattern", FailureType.BadReplacePattern),
    ],
)
def test_validation__invalid_search_pattern__failure(
    pattern_name, expected_failure_type, tmp_path: Path
):
    tmp_path.joinpath(sd.SOME_GLOB_MATCHED_FILE_NAME).touch()
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=tmp_path)
    definition = sd.some_file_definition(
        **{pattern_name: sd.SOME_INVALID_FORMAT_PATTERN}
    )

    result = validator(definition)

    assert result.failure_type == expected_failure_type
    assert sd.SOME_INVALID_FORMAT_PATTERN in result.description


def test_validation__not_search_text_single__failure(tmp_path: Path):
    expected_text = sd.some_text_formatter().format(
        sd.SOME_SEARCH_FORMAT_PATTERN, context=FormatContext.search
    )
    tmp_path.joinpath(sd.SOME_GLOB_MATCHED_FILE_NAME).touch()
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=tmp_path)
    definition = sd.some_file_definition()

    result = validator(definition)

    assert result.failure_type == FailureType.SearchPatternNotFound
    assert (
        expected_text in result.description
        and sd.SOME_GLOB_MATCHED_FILE_NAME in result.description
    )


def test_validation__not_search_text_multiple__failure(tmp_path: Path):
    expected_text = sd.some_text_formatter().format(
        sd.SOME_SEARCH_FORMAT_PATTERN, context=FormatContext.search
    )
    tmp_path.joinpath(sd.SOME_GLOB_MATCHED_FILE_NAME).write_text(expected_text)
    tmp_path.joinpath(sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME).touch()
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=tmp_path)
    definition = sd.some_file_definition()

    result = validator(definition)

    assert result.failure_type == FailureType.SearchPatternNotFound
    assert (
        expected_text in result.description
        and sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME in result.description
    )


@pytest.mark.parametrize(
    "replace_format_pattern", [sd.SOME_REPLACE_FORMAT_PATTERN, None]
)
def test_validation__search_text_found__no_failure(
    replace_format_pattern, tmp_path: Path
):
    expected_text = sd.some_text_formatter().format(
        sd.SOME_SEARCH_FORMAT_PATTERN, context=FormatContext.search
    )
    tmp_path.joinpath(sd.SOME_GLOB_MATCHED_FILE_NAME).write_text(expected_text)
    validator = DefinitionValidator(sd.SOME_VERSION, project_root=tmp_path)
    definition = sd.some_file_definition(replace_format_pattern=replace_format_pattern)

    result = validator(definition)

    assert result is None
