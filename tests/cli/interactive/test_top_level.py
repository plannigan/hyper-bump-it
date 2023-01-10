import pytest

from hyper_bump_it._cli.interactive import top_level
from hyper_bump_it._cli.interactive.top_level import TopMenu
from tests import sample_data as sd
from tests.conftest import ForceInput


def test_configure__no_initial_version__error():
    initial_config = sd.some_config_file(
        current_version=None, files=[sd.some_file_definition(keystone=True)]
    )
    with pytest.raises(ValueError):
        top_level.InteractiveConfigEditor(
            initial_config,
            sd.SOME_PYPROJECT,
            sd.SOME_PROJECT_ROOT,
        )


def test_configure__no_changes__same_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    editor = top_level.InteractiveConfigEditor(
        sd.some_config_file(), sd.SOME_PYPROJECT, sd.SOME_PROJECT_ROOT
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
        sd.some_config_file(), sd.SOME_PYPROJECT, sd.SOME_PROJECT_ROOT
    )

    result = editor.configure()[0]

    assert result == sd.some_config_file(git=other_git)


@pytest.mark.parametrize(
    ["returned_files", "expected_config"],
    [
        (
            [sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)],
            sd.some_config_file(
                files=[sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)]
            ),
        ),
        (
            [sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB, keystone=True)],
            sd.some_config_file(
                files=[
                    sd.some_file_definition(
                        file_glob=sd.SOME_OTHER_FILE_GLOB, keystone=True
                    )
                ],
                current_version=None,
            ),
        ),
    ],
)
def test_configure__files_edits__updated_config(
    returned_files, expected_config, force_input: ForceInput, mocker
):
    mocker.patch(
        "hyper_bump_it._cli.interactive.files.FilesConfigEditor.configure",
        return_value=(
            returned_files,
            any(definition.keystone for definition in returned_files),
        ),
    )
    force_input(TopMenu.Files.value, force_input.NO_INPUT)
    editor = top_level.InteractiveConfigEditor(
        sd.some_config_file(), sd.SOME_PYPROJECT, sd.SOME_PROJECT_ROOT
    )

    result = editor.configure()[0]

    assert result == expected_config


@pytest.mark.parametrize(
    [
        "confirm_prompt_response",
        "pyproject_response",
        "expected_result",
    ],
    [
        (
            "n",
            "n",
            (
                sd.some_config_file(show_confirm_prompt=True),
                False,
            ),
        ),
        (
            "y",
            "n",
            (
                sd.some_config_file(show_confirm_prompt=False),
                False,
            ),
        ),
        (
            "n",
            "y",
            (
                sd.some_config_file(show_confirm_prompt=True),
                True,
            ),
        ),
        (
            "y",
            "y",
            (
                sd.some_config_file(show_confirm_prompt=False),
                True,
            ),
        ),
    ],
)
def test_configure__general_edits__updated_general(
    confirm_prompt_response,
    pyproject_response,
    expected_result,
    force_input: ForceInput,
):
    force_input(
        TopMenu.General.value,
        confirm_prompt_response,
        pyproject_response,
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.some_config_file(), sd.SOME_PYPROJECT, sd.SOME_PROJECT_ROOT
    )

    result = editor.configure()
    assert result == expected_result


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
        sd.some_config_file(current_version=sd.SOME_VERSION),
        sd.SOME_PYPROJECT,
        sd.SOME_PROJECT_ROOT,
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
        force_input.NO_INPUT,
        "n",
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.some_config_file(show_confirm_prompt=sd.SOME_SHOW_CONFIRM_PROMPT),
        sd.SOME_PYPROJECT,
        sd.SOME_PROJECT_ROOT,
    )

    result = editor.configure()
    assert result == (
        sd.some_config_file(
            show_confirm_prompt=sd.SOME_SHOW_CONFIRM_PROMPT,
        ),
        sd.SOME_PYPROJECT,
    )


def test_configure__general_no_pyproject__pyproject_unchanged(
    force_input: ForceInput,
):
    force_input(
        "general",
        "n",
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = top_level.InteractiveConfigEditor(
        sd.some_config_file(),
        sd.SOME_PYPROJECT,
        sd.SOME_PROJECT_ROOT,
    )

    result = editor.configure()
    assert result == (
        sd.some_config_file(),
        sd.SOME_PYPROJECT,
    )
