from io import StringIO
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError, root_validator
from rich import print as r_print

from hyper_bump_it import _error as error
from hyper_bump_it._text_formatter import keys
from tests import sample_data as sd

SOME_VALID_KEYS = [keys.VERSION, keys.NEW_VERSION]
SOME_ERROR_MESSAGE = "test error message"
SOME_REF_TYPE = "test-branch"
SOME_SUB_TABLES = ("some-name", "some-sub-name")


@pytest.mark.parametrize(
    "exception",
    [
        error.BumpItError(SOME_ERROR_MESSAGE),
        error.FormatKeyError(sd.SOME_SEARCH_FORMAT_PATTERN, SOME_VALID_KEYS),
        error.FormatPatternError(sd.SOME_SEARCH_FORMAT_PATTERN, SOME_ERROR_MESSAGE),
        error.TodayFormatKeyError(sd.SOME_SEARCH_FORMAT_PATTERN, SOME_VALID_KEYS),
        error.IncompleteKeystoneVersionError(
            Path(sd.SOME_GLOB_MATCHED_FILE_NAME), sd.SOME_SEARCH_FORMAT_PATTERN
        ),
        error.FileGlobError(Path(sd.SOME_DIRECTORY_NAME), sd.SOME_FILE_GLOB),
        error.KeystoneFileGlobError(sd.SOME_FILE_GLOB, []),
        error.KeystoneFileGlobError(
            sd.SOME_FILE_GLOB,
            [sd.SOME_GLOB_MATCHED_FILE_NAME, sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME],
        ),
        error.VersionNotFound(
            Path(sd.SOME_DIRECTORY_NAME), sd.SOME_SEARCH_FORMAT_PATTERN
        ),
        error.NoRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.EmptyRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.DirtyRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.DetachedRepositoryError(Path(sd.SOME_DIRECTORY_NAME)),
        error.MissingRemoteError(sd.SOME_REMOTE, Path(sd.SOME_DIRECTORY_NAME)),
        error.AlreadyExistsError(
            SOME_REF_TYPE, sd.SOME_BRANCH, Path(sd.SOME_DIRECTORY_NAME)
        ),
        error.ConfigurationFileNotFoundError(Path(sd.SOME_DIRECTORY_NAME)),
        error.ConfigurationFileReadError(
            Path(sd.SOME_CONFIG_FILE_NAME), Exception(SOME_ERROR_MESSAGE)
        ),
        error.ConfigurationFileWriteError(
            Path(sd.SOME_CONFIG_FILE_NAME), Exception(SOME_ERROR_MESSAGE)
        ),
        error.SubTableNotExistError(Path(sd.SOME_CONFIG_FILE_NAME), SOME_SUB_TABLES),
    ],
)
def test_errors__rich_output__equivalent_to_str_representation(
    exception, capture_rich: StringIO
):
    r_print(exception)

    rich_content = capture_rich.getvalue()
    assert rich_content.strip().replace("\n", " ") == str(exception)


@pytest.mark.parametrize(
    ["description", "kwargs", "expected_content"],
    [
        (
            "single error, includes error type",
            {"foo": 1},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid: "
            "1 validation error for SomeModel\n"
            "bar\n"
            "  field required (type=value_error.missing)",
        ),
        (
            "multiple errors, list each",
            {},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid: "
            "2 validation errors for SomeModel\n"
            "foo\n"
            "  field required (type=value_error.missing)\n"
            "bar\n"
            "  field required (type=value_error.missing)",
        ),
        (
            "error below the top level object",
            {"foo": 1, "bar": {}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid: "
            "1 validation error for SomeModel\n"
            "bar -> bazz\n"
            "  field required (type=value_error.missing)",
        ),
        (
            "error at root level, location is displayed",
            {"foo": 1, "bar": {"bazz": 1}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid: "
            "1 validation error for SomeModel\n"
            "__root__\n"
            "  foo is not allowed to equal bazz (type=value_error)",
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

    assert expected_content == content


@pytest.mark.parametrize(
    ["description", "kwargs", "expected_content"],
    [
        (
            "single error",
            {"foo": 1},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "bar\n"
            "  field required\n",
        ),
        (
            "multiple errors, list each",
            {},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "2 validation errors for SomeModel\n"
            "foo\n"
            "  field required\n"
            "bar\n"
            "  field required\n",
        ),
        (
            "error below the top level object",
            {"foo": 1, "bar": {}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "bar -> bazz\n"
            "  field required\n",
        ),
        (
            "error at root level, location not displayed",
            {"foo": 1, "bar": {"bazz": 1}},
            f"The configuration file ({sd.SOME_CONFIG_FILE_NAME}) is not valid:\n"
            "1 validation error for SomeModel\n"
            "  foo is not allowed to equal bazz\n",
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

    r_print(exception)

    rich_content = capture_rich.getvalue()
    assert expected_content == rich_content


class SomeSubModel(BaseModel):
    bazz: int


class SomeModel(BaseModel):
    foo: int
    bar: SomeSubModel

    @root_validator(skip_on_failure=True)
    def check_foo_value(cls, values):
        if values["foo"] == values["bar"].bazz:
            raise ValueError("foo is not allowed to equal bazz")
        return values


def _some_validation_error(kwargs) -> ValidationError:
    try:
        SomeModel(**kwargs)
    except ValidationError as ex:
        return ex
    pytest.fail("Validation error not generated")
