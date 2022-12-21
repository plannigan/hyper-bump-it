import re
from io import StringIO
from pathlib import Path

import pytest

from hyper_bump_it import _cli as cli
from hyper_bump_it._error import BumpItError
from tests import sample_data as sd
from tests.cli.common import (
    CLI_OVERRIDE_ARGS,
    CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
    assert_failure,
    assert_success,
    runner,
)


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

    assert_failure(result, exit_code=2)
    assert re.search(expected_output_regex, result.output) is not None


def test_to__valid__args_sent_to_config_for_bump_to(mocker):
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.to.config_for_bump_to")
    mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING, *CLI_OVERRIDE_ARGS],
    )

    assert_success(result)
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
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.to.config_for_bump_to")
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

    assert_success(result)
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
    mock_config_for_bump_to = mocker.patch("hyper_bump_it._cli.to.config_for_bump_to")
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

    assert_success(result)
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
    mocker.patch("hyper_bump_it._cli.to.config_for_bump_to", return_value=app_config)
    mock_do_bump = mocker.patch("hyper_bump_it._core.do_bump")

    result = runner.invoke(cli.app, ["to", sd.SOME_VERSION_STRING])

    assert_success(result)
    mock_do_bump.assert_called_once_with(app_config)


def test_to__hyper_bump_it_error__rich_message(mocker, capture_rich: StringIO):
    mocker.patch("hyper_bump_it._cli.to.config_for_bump_to")
    mocker.patch(
        "hyper_bump_it._core.do_bump", side_effect=BumpItError(sd.SOME_ERROR_MESSAGE)
    )

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING],
    )

    assert_failure(result)
    assert sd.SOME_ERROR_MESSAGE in capture_rich.getvalue()


def test_to__other_error__no_special_handling(mocker, capture_rich: StringIO):
    mocker.patch("hyper_bump_it._cli.to.config_for_bump_to")
    mocker.patch(
        "hyper_bump_it._core.do_bump", side_effect=Exception(sd.SOME_ERROR_MESSAGE)
    )

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING],
    )

    assert_failure(result)
    assert sd.SOME_ERROR_MESSAGE not in capture_rich.getvalue()
    assert sd.SOME_ERROR_MESSAGE in str(result.exception)
