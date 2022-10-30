import pytest
from pydantic import ValidationError

from hyper_bump_it._config import file
from hyper_bump_it._text_formatter import keys

SOME_FILE_GLOB = "foo.txt"
SOME_VERSION = "1.2.3"
SOME_INVALID_OBJECT = {"not_valid_key": "some value"}
# These "non" values are chosen based on things that would be coerced into the true type
SOME_NON_STRING = 1234
SOME_NON_BOOL = 1
SOME_NON_OBJECT = "not an object with fields"


@pytest.mark.parametrize(
    ["values", "expected"],
    [
        ({key: action.value}, file.GitActions(**{key: action}))
        for action in file.GitFileAction
        for key in ("commit", "branch", "tag")
    ],
)
def test_git_actions__enum_value__created_as_enum(values, expected):
    assert file.GitActions(**values) == expected


@pytest.mark.parametrize(
    "values",
    [
        {"commit": None},
        {"branch": None},
        {"tag": None},
        {"commit": "other"},
        {"branch": "other"},
        {"tag": "other"},
        {"not_valid_key": "some value"},
    ],
)
def test_git_actions__invalid__error(values):
    with pytest.raises(ValidationError):
        file.GitActions(**values)


def test_git__no_args__valid():
    result = file.Git()

    assert result == file.Git(
        remote="origin",
        commit_format_pattern=(
            f"Bump version: {{{keys.CURRENT_VERSION}}} → {{{keys.NEW_VERSION}}}"
        ),
        branch_format_pattern=f"bump_version_to_{{{keys.NEW_VERSION}}}",
        tag_format_pattern=f"v{{{keys.NEW_VERSION}}}",
        actions=file.GitActions(),
    )


@pytest.mark.parametrize(
    ["description", "values"],
    [
        ("an invalid field name", SOME_INVALID_OBJECT),
        ("remote not a string", {"remote": SOME_NON_STRING}),
        (
            "commit_format_pattern not a string",
            {"commit_format_pattern": SOME_NON_STRING},
        ),
        (
            "branch_format_pattern not a string",
            {"branch_format_pattern": SOME_NON_STRING},
        ),
        ("tag_format_pattern not a string", {"tag_format_pattern": SOME_NON_STRING}),
        ("actions not an object", {"actions": SOME_NON_OBJECT}),
        (
            "actions is an object with invalid fields",
            {"actions": SOME_INVALID_OBJECT},
        ),
    ],
)
def test_git__invalid__error(values, description):
    with pytest.raises(ValidationError):
        file.Git(**values)


def test_file__just_file_glob__valid():
    result = file.File(file_glob=SOME_FILE_GLOB)

    assert result == file.File(
        file_glob=SOME_FILE_GLOB,
        keystone=False,
        search_format_pattern=keys.VERSION,
        replace_format_pattern=None,
    )


@pytest.mark.parametrize(
    ["description", "values"],
    [
        ("missing file glob", {}),
        ("file glob not a string", {"file_glob": SOME_NON_STRING}),
        (
            "keystone not a bool",
            {"file_glob": SOME_FILE_GLOB, "keystone": SOME_NON_BOOL},
        ),
        (
            "search format pattern not a string",
            {"file_glob": SOME_FILE_GLOB, "search_format_pattern": SOME_NON_STRING},
        ),
        (
            "replace format pattern not a string",
            {"file_glob": SOME_FILE_GLOB, "replace_format_pattern": SOME_NON_STRING},
        ),
    ],
)
def test_file__invalid__error(values, description):
    with pytest.raises(ValidationError):
        file.File(**values)


@pytest.mark.parametrize(
    ["description", "files", "current_version"],
    [
        (
            "just a single keystone file",
            [file.File(file_glob=SOME_FILE_GLOB, keystone=True)],
            None,
        ),
        (
            "a single file & current version",
            [file.File(file_glob=SOME_FILE_GLOB)],
            SOME_VERSION,
        ),
    ],
)
def test_config_file__just_files__valid(files, current_version, description):
    result = file.ConfigFile(files=files, current_version=current_version)

    assert result == file.ConfigFile(
        files=files,
        current_version=current_version,
        git=file.Git(),
    ), description


@pytest.mark.parametrize(
    ["description", "values"],
    [
        ("missing files", {}),
        ("files is empty list", {"files": []}),
        (
            "files contains an object with invalid fields",
            {"files": [SOME_INVALID_OBJECT]},
        ),
        (
            "current_version not a string",
            {"current_version": SOME_NON_STRING},
        ),
        ("git not an object", {"git": SOME_NON_OBJECT}),
        (
            "git is an object with invalid fields",
            {"git": SOME_INVALID_OBJECT},
        ),
        (
            "current_version and keystone file specified",
            {
                "current_version": SOME_VERSION,
                "files": [{"file_glob": SOME_FILE_GLOB, "keystone": True}],
            },
        ),
        (
            "no current_version or keystone file specified",
            {
                "files": [{"file_glob": SOME_FILE_GLOB}],
            },
        ),
        (
            "multiple keystone file specified",
            {
                "files": [
                    {"file_glob": SOME_FILE_GLOB, "keystone": True},
                    {"file_glob": SOME_FILE_GLOB, "keystone": True},
                ]
            },
        ),
        (
            "git is an object with invalid fields",
            {"git": SOME_INVALID_OBJECT},
        ),
    ],
)
def test_config_file__invalid__error(values, description):
    with pytest.raises(ValidationError):
        file.ConfigFile(**values)
