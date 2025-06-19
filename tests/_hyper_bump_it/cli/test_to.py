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
        ([], "Missing argument 'NEW_VERSION'"),
        (["1"], r"Invalid value for 'NEW_VERSION': .+?"),
        (
            [sd.SOME_BUMP_PART.value],
            r"Invalid value for 'NEW_VERSION': .+?",
        ),
        (
            [sd.SOME_VERSION_STRING, "--current-version", "1"],
            r"Invalid value for '--current-version'",
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
    assert re.search(expected_output_regex, result.output) is not None, result.output


def test_to__valid__args_sent_to_config_for_bump_to(mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING, *CLI_OVERRIDE_ARGS],
    )

    assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_to_args(
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
def test_to__dry_run_options__args_sent_to_config_for_bump_to(dry_run_args, mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

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
def test_to__skip_confirm_prompt_options__args_sent_to_config_for_bump_to(
    skip_confirm_prompt_args, mocker
):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

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
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
            dry_run=True,
            skip_confirm_prompt=True,
        )
    )


def test_to__valid__app_config_passed_to_do_bump(mocker):
    app_config = mocker.Mock()
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to",
        return_value=app_config,
    )
    mock_do_bump = mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(cli.app, ["to", sd.SOME_VERSION_STRING])

    assert_success(result)
    mock_do_bump.assert_called_once_with(app_config)


def test_to__hyper_bump_it_error__rich_message(mocker, capture_rich: StringIO):
    mocker.patch("hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to")
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.core.do_bump",
        side_effect=BumpItError(sd.SOME_ERROR_MESSAGE),
    )

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING],
    )

    assert_failure(result)
    assert sd.SOME_ERROR_MESSAGE in capture_rich.getvalue()


def test_to__other_error__no_special_handling(mocker, capture_rich: StringIO):
    mocker.patch("hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to")
    mocker.patch(
        "hyper_bump_it._hyper_bump_it.core.do_bump",
        side_effect=Exception(sd.SOME_ERROR_MESSAGE),
    )

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING],
    )

    assert_failure(result)
    assert sd.SOME_ERROR_MESSAGE not in capture_rich.getvalue()
    assert sd.SOME_ERROR_MESSAGE in str(result.exception)


def test_to__allowed_init_branch_not_given__not_included_in_args(mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "to",
            "--dry-run",
            sd.SOME_OTHER_VERSION_STRING,
        ],
    )

    assert_success(result)
    mock_config_for_bump_to.assert_called_once()
    assert (
        mock_config_for_bump_to.call_args.args[0].allowed_initial_branches is None
    ), result.output


def test_to__allow_any_branch__other_branches_cleared(mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "to",
            sd.SOME_OTHER_VERSION_STRING,
            *CLI_OVERRIDE_ARGS,
            # SOME_ALLOWED_BRANCH is already listed in overrides
            "--allowed-init-branch",
            sd.SOME_OTHER_ALLOWED_BRANCH,
            "--allow-any-init-branch",
        ],
    )

    assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_to_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
            dry_run=True,
            allowed_initial_branches=frozenset(),
        )
    )


@pytest.mark.parametrize(
    ["args", "names"],
    [
        (
            [
                "--allowed-init-branch",
                sd.SOME_ALLOWED_BRANCH,
                "--allowed-init-branch",
                sd.SOME_ALLOWED_BRANCH,
            ],
            f"'{sd.SOME_ALLOWED_BRANCH}'",
        ),
        (
            [
                "--allowed-init-branch",
                sd.SOME_ALLOWED_BRANCH,
                "--allowed-init-branch",
                sd.SOME_ALLOWED_BRANCH,
                "--allowed-init-branch",
                sd.SOME_OTHER_ALLOWED_BRANCH,
                "--allowed-init-branch",
                sd.SOME_OTHER_ALLOWED_BRANCH,
            ],
            f"'{sd.SOME_OTHER_ALLOWED_BRANCH}', '{sd.SOME_ALLOWED_BRANCH}'",
        ),
    ],
)
def test_to__multiple_duplicate_allowed_branches__error(
    args, names, mocker, capture_rich: StringIO
):
    mocker.patch("hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to")
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        ["to", sd.SOME_OTHER_VERSION_STRING, *args],
        catch_exceptions=False,
    )

    assert_failure(result, exit_code=2)
    assert (
        f"'allowed-init-branch' should only be given unique values. Appeared more than once: {names}"
        in str(result.output)
    )


def test_to__relative_project_root_and_config_file__resolved_paths(mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "to",
            sd.SOME_OTHER_VERSION_STRING,
            "--config-file",
            str(sd.SOME_CONFIG_FILE_NAME),
            "--project-root",
            str(sd.SOME_DIRECTORY_NAME),
        ],
    )

    assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.no_config_override_bump_to_args(
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
def test_to__patch_options__args_sent_to_config_for_bump_to(patch_args, mocker):
    mock_config_for_bump_to = mocker.patch(
        "hyper_bump_it._hyper_bump_it.cli.to.config_for_bump_to"
    )
    mocker.patch("hyper_bump_it._hyper_bump_it.core.do_bump")

    result = runner.invoke(
        cli.app,
        [
            "to",
            sd.SOME_OTHER_VERSION_STRING,
            *CLI_OVERRIDE_ARGS_WITHOUT_DRY_RUN,
            *patch_args,
        ],
    )

    assert_success(result)
    mock_config_for_bump_to.assert_called_once_with(
        sd.some_bump_to_args(
            config_file=sd.SOME_ABSOLUTE_CONFIG_FILE,
            project_root=sd.SOME_ABSOLUTE_DIRECTORY,
            patch=True,
        )
    )
