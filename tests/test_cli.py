import re
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from hyper_bump_it import _cli as cli
from tests import sample_data as sd

runner = CliRunner()

CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN: list[str] = [
    "--config-file",
    sd.SOME_CONFIG_FILE_NAME,
    "--project-root",
    sd.SOME_DIRECTORY_NAME,
    "--current-version",
    sd.SOME_OTHER_PARTIAL_VERSION_STRING,
    "--commit",
    sd.SOME_COMMIT_ACTION.value,
    "--branch",
    sd.SOME_BRANCH_ACTION.value,
    "--tag",
    sd.SOME_TAG_ACTION.value,
    "--remote",
    sd.SOME_REMOTE,
    "--commit-format-pattern",
    sd.SOME_COMMIT_PATTERN,
    "--branch-format-pattern",
    sd.SOME_BRANCH_PATTERN,
    "--tag-format-pattern",
    sd.SOME_TAG_PATTERN,
]

CLI_OVERRIDE_ARGS: list[str] = CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN + [
    "--dry-run",
]


@pytest.mark.parametrize(
    ["cli_args", "expected_output_regex"],
    [
        ([], "Missing argument 'NEW_VERSION'"),
        (["1"], r"Invalid value for NEW_VERSION: '.+?' is not a valid version"),
        (
            [sd.SOME_BUMP_PART.value],
            r"Invalid value for NEW_VERSION: '.+?' is not a valid version",
        ),
        (
            [sd.SOME_VERSION_STRING, "--current-version", "1"],
            r"Invalid value for --current-version: '.+?' is not a valid version",
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
    ],
)
def test_to__invalid__error(cli_args: list[str], expected_output_regex):
    result = runner.invoke(cli.app, ["to", *cli_args], catch_exceptions=False)

    _assert_failure(result, exit_code=2)
    assert re.search(expected_output_regex, result.output) is not None


def test_to__valid__args_sent_to_config_for_bump_to(mocker):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_to")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING, *CLI_OVERRIDE_ARGS],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_to_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
        )
    )


@pytest.mark.parametrize(
    "dry_run_args",
    [
        (["--dry-run"]),
        (["--no"]),
        (["-n"]),
        (["--dry-run", "--no-dry-run", "--dry-run"]),
    ],
)
def test_to__dry_run_options__args_sent_to_config_for_bump_to(dry_run_args, mocker):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_to")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "to",
            sd.SOME_OTHER_VERSION_STRING,
            *CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
            *dry_run_args,
        ],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_to_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
        )
    )


@pytest.mark.parametrize(
    "skip_confirm_prompt_args",
    [
        (["--yes"]),
        (["-y"]),
        (["--yes", "--interactive", "--yes"]),
    ],
)
def test_to__skip_confirm_prompt_options__args_sent_to_config_for_bump_to(
    skip_confirm_prompt_args, mocker
):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_to")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "to",
            sd.SOME_OTHER_VERSION_STRING,
            *CLI_OVERRIDE_ARGS,
            *skip_confirm_prompt_args,
        ],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_to_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
            skip_confirm_prompt=True,
        )
    )


def test_to__valid__app_config_passed_to_do_bump(mocker):
    app_config = mocker.Mock()
    mocker.patch("hyper_bump_it._cli.config_for_bump_to", return_value=app_config)
    mock_do_bump = mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(cli.app, ["to", sd.SOME_VERSION_STRING])

    _assert_success(result)
    mock_do_bump.assert_called_once_with(app_config)


@pytest.mark.parametrize(
    ["cli_args", "expected_output_regex"],
    [
        ([], "Missing argument 'PART_TO_BUMP"),
        ([sd.SOME_VERSION_STRING], r"Invalid value for 'PART_TO_BUMP"),
        (
            [sd.SOME_BUMP_PART.value, "--current-version", "1"],
            r"Invalid value for --current-version: '.+?' is not a valid version",
        ),
        (
            [sd.SOME_BUMP_PART.value, "--commit", sd.SOME_NON_GIT_ACTION_STRING],
            r"is not one of 'skip', 'create', 'create-and-push'",
        ),
        (
            [sd.SOME_BUMP_PART.value, "--branch", sd.SOME_NON_GIT_ACTION_STRING],
            r"is not one of 'skip', 'create', 'create-and-push'",
        ),
        (
            [sd.SOME_BUMP_PART.value, "--tag", sd.SOME_NON_GIT_ACTION_STRING],
            r"is not one of 'skip', 'create', 'create-and-push'",
        ),
    ],
)
def test_by__invalid__error(cli_args: list[str], expected_output_regex):
    result = runner.invoke(cli.app, ["by", *cli_args], catch_exceptions=False)

    _assert_failure(result, exit_code=2)
    assert re.search(expected_output_regex, result.output) is not None


def test_by__valid__args_sent_to_config_for_bump_by(mocker):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_by")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        ["by", sd.SOME_BUMP_PART.value, *CLI_OVERRIDE_ARGS],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
        )
    )


@pytest.mark.parametrize(
    "dry_run_args",
    [
        (["--dry-run"]),
        (["--no"]),
        (["-n"]),
        (["--dry-run", "--no-dry-run", "--dry-run"]),
    ],
)
def test_by__dry_run_options__args_sent_to_config_for_bump_by(dry_run_args, mocker):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_by")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART.value,
            *CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
            *dry_run_args,
        ],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
        )
    )


@pytest.mark.parametrize(
    "skip_confirm_prompt_args",
    [
        (["--yes"]),
        (["-y"]),
        (["--yes", "--interactive", "--yes"]),
    ],
)
def test_by__skip_confirm_prompt_options__args_sent_to_config_for_bump_by(
    skip_confirm_prompt_args, mocker
):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_by")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART.value,
            *CLI_OVERRIDE_ARGS,
            *skip_confirm_prompt_args,
        ],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
            skip_confirm_prompt=True,
        )
    )


def test_by__interactive_option__args_sent_to_config_for_bump_by(mocker):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.config_for_bump_by")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART.value,
            *CLI_OVERRIDE_ARGS,
            "--interactive",
        ],
    )

    _assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME),
            project_root=Path(sd.SOME_DIRECTORY_NAME),
            dry_run=True,
            skip_confirm_prompt=False,
        )
    )


def test_to__valid__app_config_passed_by_do_bump(mocker):
    app_config = mocker.Mock()
    mocker.patch("hyper_bump_it._cli.config_for_bump_by", return_value=app_config)
    mock_do_bump = mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(cli.app, ["by", sd.SOME_BUMP_PART.value])

    _assert_success(result)
    mock_do_bump.assert_called_once_with(app_config)


def _assert_success(result: Result) -> None:
    assert result.exit_code == 0, result.stdout


# An exit code of 1 is a general error, while 2 is for a CLI usage error. Unless the test case is checking that usage
# errors are handled, getting a 2 from a test case likely means the test case incorrectly specified the cli arguments.
def _assert_failure(result: Result, exit_code: int = 1) -> None:
    assert result.exit_code == exit_code, result.stdout
