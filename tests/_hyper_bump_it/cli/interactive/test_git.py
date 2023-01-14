from io import StringIO

from hyper_bump_it._hyper_bump_it.cli.interactive import git
from hyper_bump_it._hyper_bump_it.cli.interactive.git import GitMenu
from hyper_bump_it._hyper_bump_it.config import GitAction
from tests._hyper_bump_it import sample_data as sd
from tests.conftest import ForceInput


def test_configure__no_changes__same_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    initial_config = sd.some_git_config_file(
        remote=sd.SOME_OTHER_REMOTE, commit_format_pattern=sd.SOME_OTHER_COMMIT_PATTERN
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__remote_value__updated_remote(force_input: ForceInput):
    force_input(GitMenu.Remote.value, sd.SOME_OTHER_REMOTE, force_input.NO_INPUT)
    editor = git.GitConfigEditor(sd.some_git_config_file())

    result = editor.configure()

    assert result == sd.some_git_config_file(remote=sd.SOME_OTHER_REMOTE)


def test_configure__remote_no_input__unchanged_remote(force_input: ForceInput):
    force_input(GitMenu.Remote.value, force_input.NO_INPUT, force_input.NO_INPUT)
    initial_config = sd.some_git_config_file(remote=sd.SOME_OTHER_REMOTE)
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__commit_format_pattern_value__updated_pattern(
    force_input: ForceInput,
):
    force_input(
        GitMenu.CommitFormatPattern.value,
        sd.SOME_OTHER_COMMIT_PATTERN,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(sd.some_git_config_file())

    result = editor.configure()

    assert result == sd.some_git_config_file(
        commit_format_pattern=sd.SOME_OTHER_COMMIT_PATTERN
    )


def test_configure__commit_format_pattern_no_input__unchanged_pattern(
    force_input: ForceInput,
):
    force_input(
        GitMenu.CommitFormatPattern.value, force_input.NO_INPUT, force_input.NO_INPUT
    )
    initial_config = sd.some_git_config_file(
        commit_format_pattern=sd.SOME_OTHER_COMMIT_PATTERN
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__branch_format_pattern_value__updated_pattern(
    force_input: ForceInput,
):
    force_input(
        GitMenu.BranchFormatPattern.value,
        sd.SOME_OTHER_BRANCH_PATTERN,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(sd.some_git_config_file())

    result = editor.configure()

    assert result == sd.some_git_config_file(
        branch_format_pattern=sd.SOME_OTHER_BRANCH_PATTERN
    )


def test_configure__branch_format_pattern_no_input__unchanged_pattern(
    force_input: ForceInput,
):
    force_input(
        GitMenu.BranchFormatPattern.value, force_input.NO_INPUT, force_input.NO_INPUT
    )
    initial_config = sd.some_git_config_file(
        branch_format_pattern=sd.SOME_OTHER_BRANCH_PATTERN
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__tag_format_pattern_value__updated_pattern(
    force_input: ForceInput,
):
    force_input(
        GitMenu.TagFormatPattern.value, sd.SOME_OTHER_TAG_PATTERN, force_input.NO_INPUT
    )
    editor = git.GitConfigEditor(sd.some_git_config_file())

    result = editor.configure()

    assert result == sd.some_git_config_file(
        tag_format_pattern=sd.SOME_OTHER_TAG_PATTERN
    )


def test_configure__tag_format_pattern_no_input__unchanged_pattern(
    force_input: ForceInput,
):
    force_input(
        GitMenu.TagFormatPattern.value, force_input.NO_INPUT, force_input.NO_INPUT
    )
    initial_config = sd.some_git_config_file(
        tag_format_pattern=sd.SOME_OTHER_TAG_PATTERN
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__actions_values__updated_actions(
    force_input: ForceInput,
):
    force_input(
        GitMenu.Actions.value,
        GitAction.CreateAndPush.value,
        GitAction.Skip.value,
        GitAction.Create.value,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(sd.some_git_config_file())

    result = editor.configure()

    assert result == sd.some_git_config_file(
        actions=sd.some_git_actions_config_file(
            commit=GitAction.CreateAndPush, branch=GitAction.Skip, tag=GitAction.Create
        )
    )


def test_configure__actions_no_input__unchanged_actions(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        actions=sd.some_git_actions_config_file(
            commit=GitAction.CreateAndPush, branch=GitAction.Skip, tag=GitAction.Create
        )
    )
    force_input(
        GitMenu.Actions.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__actions_invalid_combination__ask_all_again(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        GitMenu.Actions.value,
        GitAction.Skip.value,
        GitAction.Skip.value,
        GitAction.Create.value,
        GitAction.CreateAndPush.value,
        GitAction.Skip.value,
        GitAction.Create.value,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(sd.some_git_config_file())

    result = editor.configure()

    assert result == sd.some_git_config_file(
        actions=sd.some_git_actions_config_file(
            commit=GitAction.CreateAndPush, branch=GitAction.Skip, tag=GitAction.Create
        )
    )
    assert (
        "Error: if commit is 'skip', tag must also be 'skip'" in capture_rich.getvalue()
    )
