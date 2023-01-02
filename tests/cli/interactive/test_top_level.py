"""

"""
import pytest

from hyper_bump_it._cli.interactive import top_level
from hyper_bump_it._cli.interactive.top_level import TopMenu
from tests import sample_data as sd
from tests.conftest import ForceInput


def test_configure__no_changes__same_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION, sd.some_config_file(), sd.SOME_PYPROJECT
    )

    result = editor.configure()

    assert result == (sd.some_config_file(), sd.SOME_PYPROJECT)


def test_configure__git_edits__updated_git(force_input: ForceInput, mocker):
    other_git = sd.some_git_config_file(
        remote=sd.SOME_OTHER_REMOTE, commit_format_pattern=sd.SOME_OTHER_COMMIT_PATTERN
    )
    mocker.patch(
        "hyper_bump_it._cli.interactive.git.GitConfigEditor.configure",
        return_value=other_git,
    )
    force_input(TopMenu.Git.value, force_input.NO_INPUT)
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION, sd.some_config_file(), sd.SOME_PYPROJECT
    )

    result = editor.configure()[0]

    assert result == sd.some_config_file(git=other_git)


def test_configure__files_edits__updated_git(force_input: ForceInput, mocker):
    other_files = [sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)]
    mocker.patch(
        "hyper_bump_it._cli.interactive.files.FilesConfigEditor.configure",
        return_value=other_files,
    )
    force_input(TopMenu.Files.value, force_input.NO_INPUT)
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION, sd.some_config_file(), sd.SOME_PYPROJECT
    )

    result = editor.configure()[0]

    assert result == sd.some_config_file(files=other_files)


@pytest.mark.parametrize(
    [
        "version_response",
        "confirm_prompt_response",
        "pyproject_response",
        "expected_result",
    ],
    [
        (
            sd.SOME_OTHER_VERSION_STRING,
            "n",
            "n",
            (
                sd.some_config_file(
                    current_version=sd.SOME_OTHER_VERSION, show_confirm_prompt=True
                ),
                False,
            ),
        ),
        (
            sd.SOME_OTHER_VERSION_STRING,
            "y",
            "n",
            (
                sd.some_config_file(
                    current_version=sd.SOME_OTHER_VERSION, show_confirm_prompt=False
                ),
                False,
            ),
        ),
        (
            sd.SOME_OTHER_VERSION_STRING,
            "n",
            "y",
            (
                sd.some_config_file(current_version=sd.SOME_OTHER_VERSION),
                True,
            ),
        ),
        (
            sd.SOME_OTHER_VERSION_STRING,
            "n",
            "n",
            (
                sd.some_config_file(current_version=sd.SOME_OTHER_VERSION),
                False,
            ),
        ),
    ],
)
def test_configure__general_edits__updated_general(
    version_response,
    confirm_prompt_response,
    pyproject_response,
    expected_result,
    force_input: ForceInput,
):
    force_input(
        "general",
        version_response,
        confirm_prompt_response,
        pyproject_response,
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION, sd.some_config_file(), sd.SOME_PYPROJECT
    )

    result = editor.configure()
    assert result == expected_result


def test_configure__general_invalid_version__asks_again(
    force_input: ForceInput,
):
    force_input(
        "general",
        sd.SOME_NON_VERSION_STRING,
        sd.SOME_OTHER_VERSION_STRING,
        "n",
        "n",
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION,
        sd.some_config_file(current_version=sd.SOME_VERSION),
        sd.SOME_PYPROJECT,
    )

    result = editor.configure()
    assert result == (
        sd.some_config_file(current_version=sd.SOME_OTHER_VERSION),
        sd.SOME_PYPROJECT,
    )


def test_configure__general_no_version__version_unchanged(
    force_input: ForceInput,
):
    force_input(
        "general",
        force_input.NO_INPUT,
        "n",
        "n",
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION,
        sd.some_config_file(current_version=sd.SOME_VERSION),
        sd.SOME_PYPROJECT,
    )

    result = editor.configure()
    assert result == (
        sd.some_config_file(current_version=sd.SOME_VERSION),
        sd.SOME_PYPROJECT,
    )


def test_configure__general_no_show_confirm__show_confirm_unchanged(
    force_input: ForceInput,
):
    force_input(
        "general",
        sd.SOME_OTHER_VERSION_STRING,
        force_input.NO_INPUT,
        "n",
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION,
        sd.some_config_file(show_confirm_prompt=sd.SOME_SHOW_CONFIRM_PROMPT),
        sd.SOME_PYPROJECT,
    )

    result = editor.configure()
    assert result == (
        sd.some_config_file(
            current_version=sd.SOME_OTHER_VERSION,
            show_confirm_prompt=sd.SOME_SHOW_CONFIRM_PROMPT,
        ),
        sd.SOME_PYPROJECT,
    )


def test_configure__general_no_pyproject__pyproject_unchanged(
    force_input: ForceInput,
):
    force_input(
        "general",
        sd.SOME_OTHER_VERSION_STRING,
        "n",
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.SOME_VERSION,
        sd.some_config_file(current_version=sd.SOME_VERSION),
        sd.SOME_PYPROJECT,
    )

    result = editor.configure()
    assert result == (
        sd.some_config_file(current_version=sd.SOME_OTHER_VERSION),
        sd.SOME_PYPROJECT,
    )
