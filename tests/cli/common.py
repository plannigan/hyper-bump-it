from typer.testing import CliRunner, Result

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


def assert_success(result: Result) -> None:
    assert result.exit_code == 0, result.stdout


# An exit code of 1 is a general error, while 2 is for a CLI usage error. Unless the test case is
# checking that usage errors are handled, getting a 2 from a test case likely means the test case
# incorrectly specified the cli arguments.
def assert_failure(result: Result, exit_code: int = 1) -> None:
    assert result.exit_code == exit_code, result.stdout
