import re
from io import StringIO
from pathlib import Path

import pytest
import tomlkit
from typer.testing import Result

from hyper_bump_it._hyper_bump_it import cli
from hyper_bump_it._hyper_bump_it.cli import common
from hyper_bump_it._hyper_bump_it.config import (
    HYPER_CONFIG_FILE_NAME,
    PYPROJECT_FILE_NAME,
    PYPROJECT_SUB_TABLE_KEYS,
    ROOT_TABLE_KEY,
    ConfigFile,
    FileDefinition,
    GitAction,
    file,
)
from tests._hyper_bump_it import sample_data as sd
from tests._hyper_bump_it.cli.common import assert_failure, assert_success, runner
from tests.conftest import ForceInput

PYPROJECT_ROOT_TABLE = ".".join(PYPROJECT_SUB_TABLE_KEYS)


@pytest.mark.parametrize(
    ["cli_args", "expected_output_regex"],
    [
        ([], "Missing argument 'CURRENT_VERSION'"),
        (["1"], r"Invalid value for 'CURRENT_VERSION': .+?"),
        (
            [sd.SOME_BUMP_PART.value],
            r"Invalid value for 'CURRENT_VERSION': .+?",
        ),
        (
            [sd.SOME_VERSION_STRING, "--commit", sd.SOME_NON_GIT_ACTION_STRING],
            r"is not one of 'skip', 'create', 'create-and-push'",
        ),
        (
            [sd.SOME_VERSION_STRING, "--branch", sd.SOME_NON_GIT_ACTION_STRING],
            r"is not one of 'skip', 'create', 'create-and-push'",
        ),
        (
            [sd.SOME_VERSION_STRING, "--tag", sd.SOME_NON_GIT_ACTION_STRING],
            r"is not one of 'skip', 'create', 'create-and-push'",
        ),
        (
            # example of git actions validation
            [
                sd.SOME_VERSION_STRING,
                "--commit",
                GitAction.Skip.value,
                "--branch",
                GitAction.Create.value,
            ],
            r"if commit is 'skip', branch must also be 'skip'",
        ),
    ],
)
def test_init__invalid__error(cli_args: list[str], expected_output_regex):
    result = runner.invoke(cli.app, ["init", *cli_args], catch_exceptions=False)

    assert_failure(result, exit_code=2)
    assert re.search(expected_output_regex, result.output) is not None, result.output


@pytest.mark.parametrize(
    "args",
    [
        tuple(),
        ("--allowed-init-branch", sd.SOME_ALLOWED_BRANCH),
    ],
)
def test_init___allow_any_init_branch__cancels_any_allowed_init_branch(
    args, tmp_path: Path
):
    config_file = tmp_path / HYPER_CONFIG_FILE_NAME

    result = _run_non_interactive(tmp_path, *args, "--allow-any-init-branch")

    assert_success(result)
    assert config_file.is_file()
    content = tomlkit.parse(config_file.read_text())
    assert len(content[ROOT_TABLE_KEY]["git"]["allowed_initial_branches"]) == 0
    assert "extend_allowed_initial_branches" not in content[ROOT_TABLE_KEY]["git"]


def test_init__non_interactive_dedicated__writes_file(tmp_path: Path):
    config_file = tmp_path / HYPER_CONFIG_FILE_NAME

    result = _run_non_interactive(tmp_path)

    assert_success(result)
    assert config_file.is_file()
    assert config_file.read_text() == sd.some_minimal_config_text(
        ROOT_TABLE_KEY,
        sd.SOME_VERSION_STRING,
        file_glob=common.EXAMPLE_FILE_GLOB,
        trim_empty_lines=True,
    )


def test_init__non_interactive_pyproject__writes_file(tmp_path: Path):
    config_file = tmp_path / PYPROJECT_FILE_NAME

    result = _run_non_interactive(tmp_path, "--pyproject")

    assert_success(result)
    assert config_file.is_file()
    assert config_file.read_text() == sd.some_minimal_config_text(
        PYPROJECT_ROOT_TABLE,
        sd.SOME_VERSION_STRING,
        file_glob=common.EXAMPLE_FILE_GLOB,
        trim_empty_lines=True,
    )


def test_init__non_interactive_pyproject_already_exists__content_in_file(
    tmp_path: Path,
):
    config_file = tmp_path / PYPROJECT_FILE_NAME
    config_file.write_text(tomlkit.dumps(_some_other_toml_content()))

    result = _run_non_interactive(tmp_path, "--pyproject")

    assert_success(result)
    file_content = config_file.read_text()
    assert (
        sd.some_minimal_config_text(
            PYPROJECT_ROOT_TABLE,
            sd.SOME_VERSION_STRING,
            file_glob=common.EXAMPLE_FILE_GLOB,
            trim_empty_lines=True,
        )
        in file_content
    )


def test_init__non_interactive_pyproject_already_exists__original_content_in_file(
    tmp_path: Path,
):
    config_file = tmp_path / PYPROJECT_FILE_NAME
    original_content = _some_other_toml_content()
    config_file.write_text(tomlkit.dumps(original_content))

    result = _run_non_interactive(tmp_path, "--pyproject")

    assert_success(result)
    result_content = tomlkit.parse(config_file.read_text())

    assert result_content.unwrap() == {
        "foo": 1,
        "tool": {
            "bar": {"hello": "world"},
            "hyper-bump-it": {
                "current_version": "1.2.3-11.22+b123.321",
                "files": [{"file_glob": "version.txt"}],
            },
        },
    }


def test_init__non_interactive_pyproject_invalid__error(
    tmp_path: Path, capture_rich: StringIO
):
    config_file = tmp_path / PYPROJECT_FILE_NAME
    config_file.write_text("]-ab{: not toml :'}}]]]")

    result = _run_non_interactive(tmp_path, "--pyproject")

    assert_failure(result)
    assert re.search(
        r"The configuration file .+ could not be read", capture_rich.getvalue()
    )


def test_init__interactive__defer_to_interactive(tmp_path: Path, mocker):
    interactive_config_update = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.interactive.config_update",
        return_value=(
            ConfigFile(
                current_version=sd.SOME_VERSION,
                files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
            ),
            False,
        ),
    )

    result = runner.invoke(
        cli.app,
        [
            "init",
            "--interactive",
            "--project-root",
            str(tmp_path),
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )

    assert_success(result)
    interactive_config_update.assert_called_once()


@pytest.mark.parametrize(
    ["cli_option", "pyproject_result", "expected_file_name"],
    [
        ("--pyproject", True, PYPROJECT_FILE_NAME),
        ("--pyproject", False, HYPER_CONFIG_FILE_NAME),
        ("--no-pyproject", True, PYPROJECT_FILE_NAME),
        ("--no-pyproject", False, HYPER_CONFIG_FILE_NAME),
    ],
)
def test_init__interactive__overrides_cli(
    cli_option, pyproject_result, expected_file_name, tmp_path: Path, mocker
):
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.interactive.config_update",
        return_value=(
            ConfigFile(
                current_version=sd.SOME_VERSION,
                files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
            ),
            pyproject_result,
        ),
    )

    result = runner.invoke(
        cli.app,
        [
            "init",
            "--interactive",
            cli_option,
            "--project-root",
            str(tmp_path),
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )

    assert_success(result)
    expected_file = tmp_path / expected_file_name
    assert expected_file.is_file()


@pytest.mark.parametrize(
    ["config", "expected_text"],
    [
        (
            ConfigFile(
                current_version=sd.SOME_VERSION,
                files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
            ),
            sd.some_minimal_config_text(
                ROOT_TABLE_KEY,
                sd.SOME_VERSION_STRING,
                file_glob=common.EXAMPLE_FILE_GLOB,
                trim_empty_lines=True,
            ),
        ),
        (
            ConfigFile(
                files=[
                    FileDefinition(keystone=True, file_glob=common.EXAMPLE_FILE_GLOB)
                ],
            ),
            sd.some_minimal_config_text(
                ROOT_TABLE_KEY,
                version=None,
                file_glob=common.EXAMPLE_FILE_GLOB,
                trim_empty_lines=True,
                show_confirm_prompt=None,
                include_empty_tables=False,
            ),
        ),
    ],
)
def test_init__interactive__write_out_result(
    config, expected_text, tmp_path: Path, mocker
):
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.interactive.config_update",
        return_value=(config, False),
    )
    config_file = tmp_path / HYPER_CONFIG_FILE_NAME

    result = runner.invoke(
        cli.app,
        [
            "init",
            "--interactive",
            "--project-root",
            str(tmp_path),
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )

    assert_success(result)
    assert config_file.is_file()
    assert config_file.read_text() == expected_text


@pytest.mark.parametrize(
    ["file_name", "root_table_key", "cli_args"],
    [
        (HYPER_CONFIG_FILE_NAME, file.ROOT_TABLE_KEY, []),
        (PYPROJECT_FILE_NAME, PYPROJECT_ROOT_TABLE, ["--pyproject"]),
    ],
)
def test_init__config_exists_non_interactive__fail_without_editing_file(
    file_name: str,
    root_table_key: str,
    cli_args: list["str"],
    tmp_path: Path,
):
    config_file = tmp_path / file_name
    file_text = sd.some_minimal_config_text(root_table_key, sd.SOME_VERSION_STRING)
    config_file.write_text(file_text)

    result = _run_non_interactive(tmp_path, *cli_args)

    assert_failure(result)
    assert config_file.read_text() == file_text


@pytest.mark.parametrize(
    ["file_name", "root_table_key", "cli_args", "inputs"],
    [
        (HYPER_CONFIG_FILE_NAME, file.ROOT_TABLE_KEY, [], [ForceInput.NO_INPUT, "n"]),
        (
            PYPROJECT_FILE_NAME,
            PYPROJECT_ROOT_TABLE,
            ["--pyproject"],
            [ForceInput.NO_INPUT, "n"],
        ),
    ],
)
def test_init__config_exists_interactive_no_overwrite__fail_without_editing_file(
    file_name: str,
    root_table_key: str,
    cli_args: list[str],
    inputs: list[str],
    force_input: ForceInput,
    tmp_path: Path,
):
    force_input(*inputs)
    config_file = tmp_path / file_name
    file_text = sd.some_minimal_config_text(root_table_key, sd.SOME_VERSION_STRING)
    config_file.write_text(file_text)

    result = runner.invoke(
        cli.app,
        [
            "init",
            "--interactive",
            "--project-root",
            str(tmp_path),
            *cli_args,
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )

    assert_failure(result)
    assert config_file.read_text() == file_text


def test_init__dedicated_config_exists_interactive_overwrite__file_updated(
    force_input: ForceInput,
    tmp_path: Path,
    mocker,
):
    force_input("y")
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.interactive.config_update",
        return_value=(
            ConfigFile(
                current_version=sd.SOME_VERSION,
                files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
            ),
            False,
        ),
    )
    config_file = tmp_path / HYPER_CONFIG_FILE_NAME
    file_text = sd.some_minimal_config_text(
        ROOT_TABLE_KEY, sd.SOME_OTHER_VERSION_STRING
    )
    config_file.write_text(file_text)

    result = runner.invoke(
        cli.app,
        [
            "init",
            "--interactive",
            "--project-root",
            str(tmp_path),
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )

    assert_success(result)
    assert config_file.read_text() == sd.some_minimal_config_text(
        ROOT_TABLE_KEY,
        sd.SOME_VERSION_STRING,
        file_glob=common.EXAMPLE_FILE_GLOB,
        trim_empty_lines=True,
    )


def test_init__pyproject_config_exists_interactive_overwrite__file_updated(
    force_input: ForceInput,
    tmp_path: Path,
    mocker,
):
    force_input("y")
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.interactive.config_update",
        return_value=(
            ConfigFile(
                current_version=sd.SOME_VERSION,
                files=[FileDefinition(file_glob=common.EXAMPLE_FILE_GLOB)],
            ),
            True,
        ),
    )
    config_file = tmp_path / PYPROJECT_FILE_NAME
    file_text = sd.some_minimal_config_text(
        PYPROJECT_ROOT_TABLE, sd.SOME_OTHER_VERSION_STRING
    )
    config_file.write_text(file_text)

    result = runner.invoke(
        cli.app,
        [
            "init",
            "--interactive",
            "--project-root",
            str(tmp_path),
            "--pyproject",
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )

    assert_success(result)
    assert config_file.read_text() == sd.some_minimal_config_text(
        PYPROJECT_ROOT_TABLE,
        sd.SOME_VERSION_STRING,
        file_glob=common.EXAMPLE_FILE_GLOB,
        trim_empty_lines=True,
    )


def _run_non_interactive(project_root: Path, *cli_args) -> Result:
    return runner.invoke(
        cli.app,
        [
            "init",
            "--non-interactive",
            "--project-root",
            str(project_root),
            *cli_args,
            sd.SOME_VERSION_STRING,
        ],
        catch_exceptions=False,
    )


def _some_other_toml_content() -> tomlkit.TOMLDocument:
    doc = tomlkit.TOMLDocument()
    doc["foo"] = 1
    doc["tool"] = tomlkit.table()
    doc["tool"]["bar"] = tomlkit.table()
    doc["tool"]["bar"]["hello"] = "world"
    return doc
