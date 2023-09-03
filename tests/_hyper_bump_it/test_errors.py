from io import StringIO
from pathlib import Path
from typing import Literal

import pytest
from pydantic import BaseModel, ValidationError, model_validator

from hyper_bump_it._hyper_bump_it import error, ui
from hyper_bump_it._hyper_bump_it.format_pattern import keys
from tests._hyper_bump_it import sample_data as sd

SOME_VALID_KEYS = [keys.VERSION, keys.NEW_VERSION]
SOME_ERROR_MESSAGE = "test error message"
SOME_VALIDATION_ERROR_MESSAGE = "foo is not allowed to equal bazz"
SOME_REF_TYPE: Literal["branch"] = "branch"
SOME_SUB_TABLES = ("some-name", "some-sub-name")


@pytest.mark.parametrize(
    "exception",
    [
        error.BumpItError(SOME_ERROR_MESSAGE),
        error.FormatKeyError(sd.SOME_SEARCH_FORMAT_PATTERN, SOME_VALID_KEYS),
        error.FormatKeyError(sd.SOME_ESCAPE_REQUIRED_TEXT, SOME_VALID_KEYS),
        error.FormatPatternError(sd.SOME_SEARCH_FORMAT_PATTERN, SOME_ERROR_MESSAGE),
        error.FormatPatternError(sd.SOME_ESCAPE_REQUIRED_TEXT, SOME_ERROR_MESSAGE),
        error.TodayFormatKeyError(sd.SOME_SEARCH_FORMAT_PATTERN, SOME_VALID_KEYS),
        error.TodayFormatKeyError(sd.SOME_ESCAPE_REQUIRED_TEXT, SOME_VALID_KEYS),
        error.IncompleteKeystoneVersionError(
            Path(sd.SOME_GLOB_MATCHED_FILE_NAME), sd.SOME_SEARCH_FORMAT_PATTERN
        ),
        error.IncompleteKeystoneVersionError(
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT), sd.SOME_ESCAPE_REQUIRED_TEXT
        ),
        error.FileGlobError(Path(sd.SOME_DIRECTORY_NAME), sd.SOME_FILE_GLOB),
        error.FileGlobError(
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT), sd.SOME_ESCAPE_REQUIRED_TEXT
        ),
        error.PathTraversalError(
            Path(sd.SOME_DIRECTORY_NAME),
            sd.SOME_FILE_GLOB,
            Path(sd.SOME_GLOB_MATCHED_FILE_NAME),
        ),
        error.PathTraversalError(
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT),
            sd.SOME_ESCAPE_REQUIRED_TEXT,
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT),
        ),
        error.KeystoneFileGlobError(sd.SOME_FILE_GLOB, []),
        error.KeystoneFileGlobError(
            sd.SOME_FILE_GLOB,
            [sd.SOME_GLOB_MATCHED_FILE_NAME, sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME],
        ),
        error.KeystoneFileGlobError(
            sd.SOME_ESCAPE_REQUIRED_TEXT,
            [sd.SOME_ESCAPE_REQUIRED_TEXT, sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME],
        ),
        error.VersionNotFound(
            Path(sd.SOME_DIRECTORY_NAME), sd.SOME_SEARCH_FORMAT_PATTERN
        ),
        error.SearchTextNotFound(
            Path(sd.SOME_DIRECTORY_NAME), sd.SOME_SEARCH_FORMAT_PATTERN
        ),
        error.VersionNotFound(
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT), sd.SOME_ESCAPE_REQUIRED_TEXT
        ),
        error.NoRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.NoRepositoryError(Path(sd.SOME_ESCAPE_REQUIRED_TEXT)),
        error.EmptyRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.EmptyRepositoryError(Path(sd.SOME_ESCAPE_REQUIRED_TEXT)),
        error.DirtyRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.DirtyRepositoryError(Path(sd.SOME_ESCAPE_REQUIRED_TEXT)),
        error.DetachedRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.DetachedRepositoryError(Path(sd.SOME_ESCAPE_REQUIRED_TEXT)),
        error.MissingRemoteError(sd.SOME_REMOTE, Path(sd.SOME_DIRECTORY_NAME)),
        error.MissingRemoteError(
            sd.SOME_ESCAPE_REQUIRED_TEXT, Path(sd.SOME_ESCAPE_REQUIRED_TEXT)
        ),
        error.DisallowedInitialBranchError(
            frozenset({sd.SOME_ALLOWED_BRANCH}),
            sd.SOME_BRANCH,
            Path(sd.SOME_DIRECTORY_NAME),
        ),
        error.DisallowedInitialBranchError(
            frozenset({sd.SOME_ESCAPE_REQUIRED_TEXT}),
            sd.SOME_ESCAPE_REQUIRED_TEXT,
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT),
        ),
        error.DisallowedInitialBranchError(
            frozenset({sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH}),
            sd.SOME_BRANCH,
            Path(sd.SOME_DIRECTORY_NAME),
        ),
        error.DisallowedInitialBranchError(
            frozenset({sd.SOME_ESCAPE_REQUIRED_TEXT, sd.SOME_OTHER_ALLOWED_BRANCH}),
            sd.SOME_ESCAPE_REQUIRED_TEXT,
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT),
        ),
        error.AlreadyExistsError(
            SOME_REF_TYPE, sd.SOME_BRANCH, Path(sd.SOME_DIRECTORY_NAME)
        ),
        error.AlreadyExistsError(
            SOME_REF_TYPE,
            sd.SOME_ESCAPE_REQUIRED_TEXT,
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT),
        ),
        error.ConfigurationFileNotFoundError(Path(sd.SOME_DIRECTORY_NAME)),
        error.ConfigurationFileNotFoundError(Path(sd.SOME_ESCAPE_REQUIRED_TEXT)),
        error.ConfigurationFileReadError(
            Path(sd.SOME_CONFIG_FILE_NAME), Exception(SOME_ERROR_MESSAGE)
        ),
        error.ConfigurationFileReadError(
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT), Exception(sd.SOME_ESCAPE_REQUIRED_TEXT)
        ),
        error.SubTableNotExistError(Path(sd.SOME_CONFIG_FILE_NAME), SOME_SUB_TABLES),
        error.SubTableNotExistError(
            Path(sd.SOME_ESCAPE_REQUIRED_TEXT), SOME_SUB_TABLES
        ),
    ],
)
def test_errors__rich_output__equivalent_to_str_representation(
    exception, capture_rich: StringIO
):
    ui.display(exception)

    rich_content = capture_rich.getvalue()
    assert rich_content.strip().replace("\n", " ") == str(exception)


@pytest.mark.parametrize(
    ["description", "kwargs", "expected_content"],
    [
        (
            "single error, includes error type",
            {"foo": 1},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "bar\n"
            "  Field required",
        ),
        (
            "multiple errors, list each",
            {},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "2 validation errors for SomeModel\n"
            "foo\n"
            "  Field required\n"
            "bar\n"
            "  Field required",
        ),
        (
            "error below the top level object",
            {"foo": 1, "bar": {}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "bar.bazz\n"
            "  Field required",
        ),
        (
            "error at root level, location is displayed",
            {"foo": 1, "bar": {"bazz": 1}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            f"  Value error, {SOME_VALIDATION_ERROR_MESSAGE}",
        ),
    ],
)
def test_invalid_configuration_error__str_output__expected_text(
    kwargs,
    expected_content,
    description,
):
    validation_error = _some_validation_error(kwargs)
    exception = error.InvalidConfigurationError(
        Path(sd.SOME_CONFIG_FILE_NAME), validation_error
    )

    content = str(exception)

    assert content == expected_content


@pytest.mark.parametrize(
    ["description", "kwargs", "expected_content"],
    [
        (
            "single error",
            {"foo": 1},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "bar\n"
            "  Field required\n",
        ),
        (
            "multiple errors, list each",
            {},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "2 validation errors for SomeModel\n"
            "foo\n"
            "  Field required\n"
            "bar\n"
            "  Field required\n",
        ),
        (
            "error below the top level object",
            {"foo": 1, "bar": {}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "bar.bazz\n"
            "  Field required\n",
        ),
        (
            "error at root level, location not displayed",
            {"foo": 1, "bar": {"bazz": 1}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            f"  Value error, {SOME_VALIDATION_ERROR_MESSAGE}\n",
        ),
    ],
)
def test_invalid_configuration_error__rich_output__expected_text(
    kwargs,
    expected_content,
    description,
    capture_rich: StringIO,
):
    validation_error = _some_validation_error(kwargs)
    exception = error.InvalidConfigurationError(
        Path(sd.SOME_CONFIG_FILE_NAME), validation_error
    )

    ui.display(exception)

    rich_content = capture_rich.getvalue()
    assert rich_content == expected_content


def test_invalid_configuration_error__rich_output_escape_required__expected_text(
    capture_rich: StringIO,
):
    validation_error = _some_validation_error({"foo": 1})
    exception = error.InvalidConfigurationError(
        Path(sd.SOME_ESCAPE_REQUIRED_TEXT), validation_error
    )

    ui.display(exception)

    rich_content = capture_rich.getvalue()
    expected_content = (
        f"The configuration file ({sd.SOME_ESCAPE_REQUIRED_TEXT}) is not valid:\n"
        "1 validation error for SomeModel\n"
        "bar\n"
        "  Field required\n"
    )
    assert expected_content == rich_content


@pytest.mark.parametrize(
    ["args", "expected_message"],
    [
        # no context for pydantic native validation
        ({"foo": 1}, "Field required"),
        # context for custom validation
        ({"foo": 1, "bar": {"bazz": 1}}, SOME_VALIDATION_ERROR_MESSAGE),
    ],
)
def test_first_error__context_exists__exception_message(args, expected_message):
    validation_error = _some_validation_error(args)

    message = error.first_error_message(validation_error)
    assert message == expected_message


class SomeSubModel(BaseModel):
    bazz: int


class SomeModel(BaseModel):
    foo: int
    bar: SomeSubModel

    @model_validator(mode="after")
    def check_foo_value(self) -> "SomeModel":
        if self.foo == self.bar.bazz:
            raise ValueError(SOME_VALIDATION_ERROR_MESSAGE)
        return self


def _some_validation_error(kwargs: dict[str, object]) -> ValidationError:
    try:
        SomeModel(**kwargs)
    except ValidationError as ex:
        return ex
    pytest.fail("Validation error not generated")
