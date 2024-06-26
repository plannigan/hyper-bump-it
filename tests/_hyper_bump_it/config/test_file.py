from pathlib import Path
from textwrap import dedent

import pytest
from pydantic import ValidationError

from hyper_bump_it._hyper_bump_it.config import GitAction, file
from hyper_bump_it._hyper_bump_it.config.core import DEFAULT_SEARCH_PATTERN
from hyper_bump_it._hyper_bump_it.error import (
    ConfigurationFileNotFoundError,
    ConfigurationFileReadError,
    InvalidConfigurationError,
    SubTableNotExistError,
)
from hyper_bump_it._hyper_bump_it.format_pattern import FormatContext, keys
from tests._hyper_bump_it import sample_data as sd
from tests._hyper_bump_it.git_action_combinations import (
    INVALID_COMBINATIONS,
    GitActionCombination,
)

PYPROJECT_ROOT_TABLE = ".".join(file.PYPROJECT_SUB_TABLE_KEYS)
SOME_INVALID_OBJECT = {"not_valid_key": "some value"}
# These "non" values are chosen based on things that would be coerced into the true type
SOME_NON_STRING = 1234
SOME_NON_BOOL = 1
SOME_NON_OBJECT = "not an object with fields"


def _gen_enum_value_parameters() -> list[tuple[dict[str, str], file.GitActions]]:
    parameters = []
    for action in iter(GitAction):
        for key in ("commit", "branch", "tag"):
            if action == GitAction.CreateAndPush and key in ("branch", "tag"):
                param = (
                    {"commit": GitAction.CreateAndPush.value, key: action.value}
                ), file.GitActions(commit=GitAction.CreateAndPush, **{key: action})
            else:
                param = (
                    {key: action.value},
                    file.GitActions(**{key: action}),
                )
            parameters.append(param)
    return parameters


@pytest.mark.parametrize(
    ["values", "expected"],
    _gen_enum_value_parameters(),
)
def test_git_actions__enum_value__created_as_enum(values, expected):
    assert file.GitActions(**values) == expected


@pytest.mark.parametrize(
    "values",
    [
        {"commit": None},
        {"branch": None},
        {"tag": None},
        {"commit": sd.SOME_NON_GIT_ACTION_STRING},
        {"branch": sd.SOME_NON_GIT_ACTION_STRING},
        {"tag": sd.SOME_NON_GIT_ACTION_STRING},
        {"not_valid_key": "some value"},
    ],
)
def test_git_actions__invalid__error(values):
    with pytest.raises(ValidationError):
        file.GitActions(**values)


@pytest.mark.parametrize(["invalid_combination", "match"], INVALID_COMBINATIONS)
def test_git_actions__invalid_combination__error(
    invalid_combination: GitActionCombination, match: str
):
    with pytest.raises(ValidationError, match=match):
        file.GitActions(**invalid_combination)


def test_git__no_args__valid():
    result = file.Git()

    assert result == file.Git(
        remote="origin",
        commit_format_pattern=(
            f"Bump version: {{{keys.CURRENT_VERSION}}} → {{{keys.NEW_VERSION}}}"
        ),
        branch_format_pattern=f"bump_version_to_{{{keys.NEW_VERSION}}}",
        tag_name_format_pattern=f"v{{{keys.NEW_VERSION}}}",
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
        (
            "tag_name_format_pattern not a string",
            {"tag_name_format_pattern": SOME_NON_STRING},
        ),
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
    result = file.File(file_glob=sd.SOME_FILE_GLOB)

    assert result == file.File(
        file_glob=sd.SOME_FILE_GLOB,
        keystone=False,
        search_format_pattern=DEFAULT_SEARCH_PATTERN,
        replace_format_pattern=None,
    )


def test_file__default_search_pattern__formats_to_version():
    search_pattern = file.File(file_glob=sd.SOME_FILE_GLOB).search_format_pattern

    formatted_search_text = sd.some_text_formatter().format(
        search_pattern, FormatContext.search
    )

    assert formatted_search_text == sd.SOME_VERSION_STRING


@pytest.mark.parametrize(
    ["description", "values"],
    [
        ("missing file glob", {}),
        ("file glob not a string", {"file_glob": SOME_NON_STRING}),
        (
            "keystone not a bool",
            {"file_glob": sd.SOME_FILE_GLOB, "keystone": SOME_NON_BOOL},
        ),
        (
            "search format pattern not a string",
            {"file_glob": sd.SOME_FILE_GLOB, "search_format_pattern": SOME_NON_STRING},
        ),
        (
            "replace format pattern not a string",
            {"file_glob": sd.SOME_FILE_GLOB, "replace_format_pattern": SOME_NON_STRING},
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
            [file.File(file_glob=sd.SOME_FILE_GLOB, keystone=True)],
            None,
        ),
        (
            "a single file & current version",
            [file.File(file_glob=sd.SOME_FILE_GLOB)],
            sd.SOME_VERSION_STRING,
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
    ["description", "files", "current_version", "expected"],
    [
        (
            "a single keystone file",
            [
                file.File(
                    file_glob=sd.SOME_FILE_GLOB,
                    keystone=True,
                    search_format_pattern=sd.SOME_SEARCH_FORMAT_PATTERN,
                )
            ],
            None,
            (sd.SOME_FILE_GLOB, sd.SOME_SEARCH_FORMAT_PATTERN),
        ),
        (
            "a single file & current version",
            [file.File(file_glob=sd.SOME_FILE_GLOB)],
            sd.SOME_VERSION_STRING,
            None,
        ),
    ],
)
def test_config_file__keystone_config_based_on_file__expected_result(
    files, current_version, expected, description
):
    result = file.ConfigFile(files=files, current_version=current_version)

    assert result.keystone_config == expected, description


def test_config_file__current_version_already_parsed__valid():
    files = [file.File(file_glob=sd.SOME_FILE_GLOB)]
    result = file.ConfigFile(files=files, current_version=sd.SOME_VERSION)

    assert result == file.ConfigFile(
        files=files,
        current_version=sd.SOME_VERSION,
        git=file.Git(),
    )


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
                "current_version": sd.SOME_VERSION_STRING,
                "files": [{"file_glob": sd.SOME_FILE_GLOB, "keystone": True}],
            },
        ),
        (
            "no current_version or keystone file specified",
            {
                "files": [{"file_glob": sd.SOME_FILE_GLOB}],
            },
        ),
        (
            "multiple keystone file specified",
            {
                "files": [
                    {"file_glob": sd.SOME_FILE_GLOB, "keystone": True},
                    {"file_glob": sd.SOME_FILE_GLOB, "keystone": True},
                ]
            },
        ),
        (
            "git is an object with invalid fields",
            {
                "git": SOME_INVALID_OBJECT,
                "current_version": sd.SOME_VERSION_STRING,
                "files": [{"file_glob": sd.SOME_FILE_GLOB}],
            },
        ),
        (
            "show_confirm_prompt not bool",
            {
                "current_version": sd.SOME_VERSION_STRING,
                "files": [{"file_glob": sd.SOME_FILE_GLOB}],
                "show_confirm_prompt": SOME_NON_BOOL,
            },
        ),
    ],
)
def test_config_file__invalid__error(values, description):
    with pytest.raises(ValidationError):
        file.ConfigFile(**values)


def test_read_pyproject_config__not_a_file__error(tmp_path: Path):
    with pytest.raises(ConfigurationFileReadError):
        file.read_pyproject_config(tmp_path, sd.SOME_PROJECT_ROOT)


def test_read_config__config_file_given__read_hyper_config_file_ignoring_project_root(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, sd.SOME_VERSION_STRING)
    )
    some_other_dir = tmp_path / "other_dir"
    some_other_dir.mkdir()

    config, _ = file.read_config(config_file, project_root=some_other_dir)

    assert config == file.ConfigFile(
        current_version=sd.SOME_VERSION_STRING,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB)],
    )


@pytest.mark.parametrize(
    ["filename", "root_table"],
    [
        (file.HYPER_CONFIG_FILE_NAME, file.ROOT_TABLE_KEY),
        (file.PYPROJECT_FILE_NAME, PYPROJECT_ROOT_TABLE),
    ],
)
def test_read_config__project_dir_given__read_from_given_dir(
    filename: str, root_table: str, tmp_path: Path
):
    config_file = tmp_path / filename
    config_file.write_text(
        sd.some_minimal_config_text(root_table, sd.SOME_VERSION_STRING)
    )

    config, _ = file.read_config(config_file=None, project_root=tmp_path)

    assert config == file.ConfigFile(
        current_version=sd.SOME_VERSION_STRING,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB)],
    )


def test_read_config__dedicated_and_pyproject__prefer_dedicated(tmp_path: Path):
    config_file = tmp_path / file.HYPER_CONFIG_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, sd.SOME_VERSION_STRING)
    )
    config_file = tmp_path / file.PYPROJECT_FILE_NAME
    config_file.write_text(
        sd.some_minimal_config_text(
            file.PYPROJECT_SUB_TABLE_KEYS, sd.SOME_OTHER_VERSION_STRING
        )
    )

    config, _ = file.read_config(config_file=None, project_root=tmp_path)

    assert config == file.ConfigFile(
        current_version=sd.SOME_VERSION_STRING,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB)],
    )


def test_read_config__no_file__error(tmp_path: Path):
    with pytest.raises(ConfigurationFileNotFoundError):
        file.read_config(config_file=None, project_root=tmp_path)


def test_read_pyproject_config__invalid_toml__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text("{-not valid{")

    with pytest.raises(ConfigurationFileReadError):
        file.read_pyproject_config(config_file, sd.SOME_PROJECT_ROOT)


def test_read_pyproject_config__sub_table_missing__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text("[foo]")

    with pytest.raises(SubTableNotExistError):
        file.read_pyproject_config(config_file, sd.SOME_PROJECT_ROOT)


def test_read_pyproject_config__configuration_invalid__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(
        dedent(
            f"""\
        [{PYPROJECT_ROOT_TABLE}]
"""
        )
    )

    with pytest.raises(InvalidConfigurationError):
        file.read_pyproject_config(config_file, sd.SOME_PROJECT_ROOT)


def test_read_pyproject_config__valid_current_version__config_returned(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(
        sd.some_minimal_config_text(PYPROJECT_ROOT_TABLE, sd.SOME_VERSION_STRING)
    )

    config, updater = file.read_pyproject_config(config_file, sd.SOME_PROJECT_ROOT)

    assert config == file.ConfigFile(
        current_version=sd.SOME_VERSION_STRING,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB)],
    )


def test_read_pyproject_config__valid_current_version__returned_updater_produces_planned_change(
    tmp_path: Path,
):
    project_root = tmp_path
    config_file = project_root / sd.SOME_CONFIG_FILE_NAME
    original_text = sd.some_minimal_config_text(
        PYPROJECT_ROOT_TABLE, sd.SOME_VERSION_STRING
    )

    config_file.write_text(original_text)

    config, updater = file.read_pyproject_config(config_file, project_root)

    assert updater is not None
    result = updater(sd.SOME_OTHER_VERSION)

    assert result == sd.some_planned_change(
        config_file,
        project_root,
        old_content=original_text,
        new_content=sd.some_minimal_config_text(
            PYPROJECT_ROOT_TABLE,
            sd.SOME_OTHER_VERSION_STRING,
        ),
        newline="\n",
    )


def test_read_pyproject_config__valid_keystone__config_returned(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(sd.some_minimal_config_text(PYPROJECT_ROOT_TABLE, None))

    config, updater = file.read_pyproject_config(config_file, sd.SOME_PROJECT_ROOT)

    assert config == file.ConfigFile(
        current_version=None,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB, keystone=True)],
    )


def test_read_pyproject_config__valid_keystone__no_updater_returned(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(sd.some_minimal_config_text(PYPROJECT_ROOT_TABLE, None))

    config, updater = file.read_pyproject_config(config_file, sd.SOME_PROJECT_ROOT)

    assert updater is None


def test_read_hyper_config__not_a_file__error(tmp_path: Path):
    with pytest.raises(ConfigurationFileReadError):
        file.read_hyper_config(tmp_path, sd.SOME_PROJECT_ROOT)


def test_read_hyper_config__invalid_toml__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text("{-not valid{")

    with pytest.raises(ConfigurationFileReadError):
        file.read_hyper_config(config_file, sd.SOME_PROJECT_ROOT)


def test_read_hyper_config__sub_table_missing__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text("[foo]")

    with pytest.raises(SubTableNotExistError):
        file.read_hyper_config(config_file, sd.SOME_PROJECT_ROOT)


def test_read_hyper_config__configuration_invalid__error(tmp_path: Path):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(
        dedent(
            f"""\
        [{file.ROOT_TABLE_KEY}]
"""
        )
    )

    with pytest.raises(InvalidConfigurationError):
        file.read_hyper_config(config_file, sd.SOME_PROJECT_ROOT)


def test_read_hyper_config__valid_current_version__config_returned(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(
        sd.some_minimal_config_text(file.ROOT_TABLE_KEY, sd.SOME_VERSION_STRING)
    )

    config, updater = file.read_hyper_config(config_file, sd.SOME_PROJECT_ROOT)

    assert config == file.ConfigFile(
        current_version=sd.SOME_VERSION_STRING,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB)],
    )


def test_read_hyper_config__valid_current_version__returned_updater_updates_file(
    tmp_path: Path,
):
    project_root = tmp_path
    config_file = project_root / sd.SOME_CONFIG_FILE_NAME
    original_text = sd.some_minimal_config_text(
        file.ROOT_TABLE_KEY, sd.SOME_VERSION_STRING
    )

    config_file.write_text(original_text)

    config, updater = file.read_hyper_config(config_file, project_root=tmp_path)

    assert updater is not None
    result = updater(sd.SOME_OTHER_VERSION)

    assert result == sd.some_planned_change(
        config_file,
        project_root,
        old_content=original_text,
        new_content=sd.some_minimal_config_text(
            file.ROOT_TABLE_KEY,
            sd.SOME_OTHER_VERSION_STRING,
        ),
        newline="\n",
    )


def test_read_hyper_config__crlf_newline__newline_as_crlf(
    tmp_path: Path,
):
    project_root = tmp_path
    config_file = project_root / sd.SOME_CONFIG_FILE_NAME
    original_text = sd.some_minimal_config_text(
        file.ROOT_TABLE_KEY, sd.SOME_VERSION_STRING, crlf_newline=True
    )

    config_file.write_text(original_text)

    config, updater = file.read_hyper_config(config_file, project_root=tmp_path)

    assert updater is not None
    result = updater(sd.SOME_OTHER_VERSION)

    assert result == sd.some_planned_change(
        config_file,
        project_root,
        old_content=original_text,
        new_content=sd.some_minimal_config_text(
            file.ROOT_TABLE_KEY, sd.SOME_OTHER_VERSION_STRING, crlf_newline=True
        ),
        newline="\r\n",
    )


def test_read_hyper_config__valid_keystone__config_returned(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(sd.some_minimal_config_text(file.ROOT_TABLE_KEY, None))

    config, updater = file.read_hyper_config(config_file, sd.SOME_PROJECT_ROOT)

    assert config == file.ConfigFile(
        current_version=None,
        files=[file.File(file_glob=sd.SOME_FILE_GLOB, keystone=True)],
    )


def test_read_hyper_config__valid_keystone__no_updater_returned(
    tmp_path: Path,
):
    config_file = tmp_path / sd.SOME_CONFIG_FILE_NAME

    config_file.write_text(sd.some_minimal_config_text(file.ROOT_TABLE_KEY, None))

    config, updater = file.read_hyper_config(config_file, sd.SOME_PROJECT_ROOT)

    assert updater is None
