import re
from io import StringIO
from pathlib import Path

import pytest

from hyper_bump_it._hyper_bump_it import cli
from hyper_bump_it._hyper_bump_it.error import BumpItError
from tests._hyper_bump_it import sample_data as sd
from tests._hyper_bump_it.cli.common import (
    CLI_OVERRIDE_ARGS,
    CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
    assert_failure,
    assert_success,
    runner,
)


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

    assert_failure(result, exit_code=2)
    assert re.search(expected_output_regex, result.output) is not None


def test_by__valid__args_sent_to_config_for_bump_by(mocker):
    mock_config_for_bump_by = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        ["by", sd.SOME_BUMP_PART.value, *CLI_OVERRIDE_ARGS],
    )

    assert_success(result)
    mock_config_for_bump_by.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
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
    mock_config_for_bump_by = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART.value,
            *CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
            *dry_run_args,
        ],
    )

    assert_success(result)
    mock_config_for_bump_by.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
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
    mock_config_for_bump_by = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART.value,
            *CLI_OVERRIDE_ARGS,
            *skip_confirm_prompt_args,
        ],
    )

    assert_success(result)
    mock_config_for_bump_by.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
            dry_run=True,
            skip_confirm_prompt=True,
        )
    )


def test_by__interactive_option__args_sent_to_config_for_bump_by(mocker):
    mock_config_for_bump_by = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART.value,
            *CLI_OVERRIDE_ARGS,
            "--interactive",
        ],
    )

    assert_success(result)
    mock_config_for_bump_by.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
            dry_run=True,
            skip_confirm_prompt=False,
        )
    )


def test_by__valid__app_config_passed_by_do_bump(mocker):
    app_config = mocker.Mock()
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by",
        return_value=app_config,
    )
    mock_do_bump = mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(cli.app, ["by", sd.SOME_BUMP_PART.value])

    assert_success(result)
    mock_do_bump.assert_called_once_with(app_config)


def test_by__hyper_bump_it_error__rich_message(mocker, capture_rich: StringIO):
    mocker.patch("hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by")
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.core.do_bump",
        side_effect=BumpItError(sd.SOME_ERROR_MESSAGE),
    )

    result = runner.invoke(
        cli.app,
        ["by", sd.SOME_BUMP_PART.value],
    )

    assert_failure(result)
    assert sd.SOME_ERROR_MESSAGE in capture_rich.getvalue()


def test_by__other_error__no_special_handling(mocker, capture_rich: StringIO):
    mocker.patch("hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by")
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.core.do_bump",
        side_effect=Exception(sd.SOME_ERROR_MESSAGE),
    )

    result = runner.invoke(
        cli.app,
        ["by", sd.SOME_BUMP_PART.value],
    )

    assert_failure(result)
    assert sd.SOME_ERROR_MESSAGE not in capture_rich.getvalue()
    assert sd.SOME_ERROR_MESSAGE in str(result.exception)


def test_tby__relative_project_root_and_config_file__resolved_paths(mocker):
    mock_config_for_bump_by = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART,
            "--config-file",
            str(sd.SOME_CONFIG_FILE_NAME),
            "--project-root",
            str(sd.SOME_DIRECTORY_NAME),
        ],
    )

    assert_success(result)
    mock_config_for_bump_by.assert_called_once_with(
        sd.no_config_override_bump_by_args(
            config_file=Path(sd.SOME_CONFIG_FILE_NAME).resolve(),
            project_root=Path(sd.SOME_DIRECTORY_NAME).resolve(),
        )
    )


@pytest.mark.parametrize(
    "patch_args",
    [
        (["--patch"]),
        (["--patch", "--no-patch", "--patch"]),
    ],
)
def test_by__patch_options__args_sent_to_config_for_bump_to(patch_args, mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.by.config_for_bump_by"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "by",
            sd.SOME_BUMP_PART,
            *CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
            *patch_args,
        ],
    )

    assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_by_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
            patch=True,
        )
    )
