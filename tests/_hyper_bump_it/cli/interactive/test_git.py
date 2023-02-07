from io import StringIO

import pytest

from hyper_bump_it._hyper_bump_it.cli.interactive import git
from hyper_bump_it._hyper_bump_it.cli.interactive.git import (
    AllowedBranchesMenu,
    GitMenu,
)
from hyper_bump_it._hyper_bump_it.config import (
    DEFAULT_ALLOWED_INITIAL_BRANCHES,
    GitAction,
)
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


def test_configure__remote_require_escape__values_escaped(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        GitMenu.Remote.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(
        sd.some_git_config_file(remote=sd.SOME_ESCAPE_REQUIRED_TEXT)
    )

    editor.configure()

    assert sd.SOME_ESCAPE_REQUIRED_TEXT in capture_rich.getvalue()


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


def test_configure__commit_format_pattern_require_escape__values_escaped(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        GitMenu.CommitFormatPattern.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(
        sd.some_git_config_file(commit_format_pattern=sd.SOME_ESCAPE_REQUIRED_TEXT)
    )

    editor.configure()

    assert sd.SOME_ESCAPE_REQUIRED_TEXT in capture_rich.getvalue()


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


def test_configure__branch_format_pattern_require_escape__values_escaped(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        GitMenu.BranchFormatPattern.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(
        sd.some_git_config_file(branch_format_pattern=sd.SOME_ESCAPE_REQUIRED_TEXT)
    )

    editor.configure()

    assert sd.SOME_ESCAPE_REQUIRED_TEXT in capture_rich.getvalue()


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


def test_configure__tag_format_pattern_require_escape__values_escaped(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        GitMenu.TagFormatPattern.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(
        sd.some_git_config_file(tag_format_pattern=sd.SOME_ESCAPE_REQUIRED_TEXT)
    )

    editor.configure()

    assert sd.SOME_ESCAPE_REQUIRED_TEXT in capture_rich.getvalue()


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


def test_configure_allowed_branches__no_input__unchanged_branches(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure_allowed_branches__add_no_name__unchanged_branches(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Add.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure_allowed_branches__add_duplicate__unchanged_branches(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Add.value,
        sd.SOME_ALLOWED_BRANCH,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure_allowed_branches__add_new_duplicate__new_branch_added(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Add.value,
        sd.SOME_ALLOWED_BRANCH,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )


def test_configure_allowed_branches__remove_empty__unchanged_branches(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches=set(), extend_allowed_initial_branches=set()
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Remove.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure_allowed_branches__remove_single__no_branches(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Remove.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == sd.some_git_config_file(
        allowed_initial_branches=set(), extend_allowed_initial_branches=set()
    )


def test_configure_allowed_branches__remove_multiple__given_branch_removed(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Remove.value,
        sd.SOME_ALLOWED_BRANCH,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )


def test_configure_allowed_branches__clear__no_branches(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches={sd.SOME_ALLOWED_BRANCH, sd.SOME_OTHER_ALLOWED_BRANCH},
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Clear.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == sd.some_git_config_file(
        allowed_initial_branches=set(), extend_allowed_initial_branches=set()
    )


def test_configure_allowed_branches__start_default_not_changes__same_values(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches=DEFAULT_ALLOWED_INITIAL_BRANCHES,
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Done.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure_allowed_branches__start_default_add_one__new_value_in_extend(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches=DEFAULT_ALLOWED_INITIAL_BRANCHES,
        extend_allowed_initial_branches=set(),
    )
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Add.value,
        sd.SOME_ALLOWED_BRANCH,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == sd.some_git_config_file(
        allowed_initial_branches=DEFAULT_ALLOWED_INITIAL_BRANCHES,
        extend_allowed_initial_branches={sd.SOME_ALLOWED_BRANCH},
    )


def test_configure_allowed_branches__start_default_remove_one__remaining_allowed(
    force_input: ForceInput,
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches=DEFAULT_ALLOWED_INITIAL_BRANCHES,
        extend_allowed_initial_branches=set(),
    )
    to_remove, to_remain = DEFAULT_ALLOWED_INITIAL_BRANCHES
    force_input(
        GitMenu.AllowedBranches.value,
        AllowedBranchesMenu.Remove.value,
        to_remove,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    result = editor.configure()

    assert result == sd.some_git_config_file(
        allowed_initial_branches={to_remain},
        extend_allowed_initial_branches=set(),
    )


@pytest.mark.parametrize(
    "branches",
    [
        {sd.SOME_ESCAPE_REQUIRED_TEXT},
        {sd.SOME_ESCAPE_REQUIRED_TEXT, sd.SOME_OTHER_ESCAPE_REQUIRED_TEXT},
    ],
)
def test_configure_allowed_branches__require_escape__values_escaped(
    branches, force_input: ForceInput, capture_rich: StringIO
):
    initial_config = sd.some_git_config_file(
        allowed_initial_branches=branches,
    )
    force_input(
        GitMenu.AllowedBranches.value,
        force_input.NO_INPUT,
        force_input.NO_INPUT,
    )
    editor = git.GitConfigEditor(initial_config)

    editor.configure()

    output = capture_rich.getvalue()
    for branch in branches:
        assert branch in output


@pytest.mark.parametrize(
    ["value", "default", "expected_output"],
    [
        ("a", "b", ""),
        ("a", "a", " (the default)"),
    ],
)
def test_default_message__expected_output(value, default, expected_output):
    result = git._default_message(value, default)

    assert result.plain == expected_output
