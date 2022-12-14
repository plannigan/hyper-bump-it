from datetime import datetime
from io import StringIO
from itertools import zip_longest
from pathlib import Path
from typing import Type

import pytest

from hyper_bump_it import _execution_plan as execution_plan
from hyper_bump_it._config import GitAction
from tests import sample_data as sd

SOME_EXECUTION_DESCRIPTION = "test description"
SOME_INTENT_DESCRIPTION = "test intent description"


def test_action_group_call__call_sub_actions(mocker):
    some_action = mocker.Mock()
    some_other_action = mocker.Mock()
    action_group = execution_plan.ActionGroup(
        intent_description=SOME_INTENT_DESCRIPTION,
        execution_description=SOME_EXECUTION_DESCRIPTION,
        actions=[some_action, some_other_action],
    )

    action_group()

    some_action.assert_called_once_with()
    some_other_action.assert_called_once_with()


def test_action_group_call__call_sub_actions_in_order(mocker):
    some_action_call_time = None
    some_other_action_call_time = None

    def _some_action():
        nonlocal some_action_call_time
        some_action_call_time = datetime.now()

    some_action = mocker.Mock(side_effect=_some_action)

    def _some_other_action():
        nonlocal some_other_action_call_time
        some_other_action_call_time = datetime.now()

    some_other_action = mocker.Mock(side_effect=_some_other_action)

    action_group = execution_plan.ActionGroup(
        intent_description=SOME_INTENT_DESCRIPTION,
        execution_description=SOME_EXECUTION_DESCRIPTION,
        actions=[some_action, some_other_action],
    )

    action_group()

    assert some_other_action_call_time > some_action_call_time


def test_action_group_call__description_displayed(capture_rich: StringIO, mocker):
    some_action = mocker.Mock()
    action_group = execution_plan.ActionGroup(
        intent_description=SOME_INTENT_DESCRIPTION,
        execution_description=SOME_EXECUTION_DESCRIPTION,
        actions=[some_action],
    )

    action_group()

    assert SOME_EXECUTION_DESCRIPTION in capture_rich.getvalue()


def test_action_group_display__call_sub_actions(mocker):
    some_action = mocker.Mock()
    some_other_action = mocker.Mock()
    action_group = execution_plan.ActionGroup(
        intent_description=SOME_INTENT_DESCRIPTION,
        execution_description=SOME_EXECUTION_DESCRIPTION,
        actions=[some_action, some_other_action],
    )

    action_group.display_intent()

    some_action.display_intent.assert_called_once_with()
    some_other_action.display_intent.assert_called_once_with()


def test_action_group_display__call_sub_actions_in_order(mocker):
    some_action_call_time = None
    some_other_action_call_time = None

    def _some_action():
        nonlocal some_action_call_time
        some_action_call_time = datetime.now()

    some_action = mocker.Mock()
    some_action.display_intent.side_effect = _some_action

    def _some_other_action():
        nonlocal some_other_action_call_time
        some_other_action_call_time = datetime.now()

    some_other_action = mocker.Mock()
    some_other_action.display_intent.side_effect = _some_other_action

    action_group = execution_plan.ActionGroup(
        intent_description=SOME_INTENT_DESCRIPTION,
        execution_description=SOME_EXECUTION_DESCRIPTION,
        actions=[some_action, some_other_action],
    )

    action_group.display_intent()

    assert some_other_action_call_time > some_action_call_time


def test_action_group_display__description_displayed(capture_rich: StringIO, mocker):
    some_action = mocker.Mock()
    action_group = execution_plan.ActionGroup(
        intent_description=SOME_INTENT_DESCRIPTION,
        execution_description=SOME_EXECUTION_DESCRIPTION,
        actions=[some_action],
    )

    action_group.display_intent()

    assert SOME_INTENT_DESCRIPTION in capture_rich.getvalue()


def test_execution_plan__add_action__execute_calls_action(mocker):
    plan = execution_plan.ExecutionPlan()
    some_action = mocker.Mock()
    plan.add_action(some_action)

    plan.execute_plan()

    some_action.assert_called_once_with()


def test_execution_plan__add_actions__execute_calls_actions(mocker):
    plan = execution_plan.ExecutionPlan()
    some_action = mocker.Mock()
    some_other_action = mocker.Mock()
    plan.add_actions([some_action, some_other_action])

    plan.execute_plan()

    some_action.assert_called_once_with()
    some_other_action.assert_called_once_with()


def test_execution_plan__add_actions__execute_actions_in_order(mocker):
    some_action_call_time = None
    some_other_action_call_time = None

    def _some_action():
        nonlocal some_action_call_time
        some_action_call_time = datetime.now()

    some_action = mocker.Mock(side_effect=_some_action)

    def _some_other_action():
        nonlocal some_other_action_call_time
        some_other_action_call_time = datetime.now()

    some_other_action = mocker.Mock(side_effect=_some_other_action)

    plan = execution_plan.ExecutionPlan()
    plan.add_actions([some_action, some_other_action])

    plan.execute_plan()

    assert some_other_action_call_time > some_action_call_time


def test_execution_plan__add_action__display_calls_action(mocker):
    plan = execution_plan.ExecutionPlan()
    some_action = mocker.Mock()
    plan.add_action(some_action)

    plan.display_plan()

    some_action.display_intent.assert_called_once_with()


def test_execution_plan__add_actions__display_calls_actions(mocker):
    plan = execution_plan.ExecutionPlan()
    some_action = mocker.Mock()
    some_other_action = mocker.Mock()
    plan.add_actions([some_action, some_other_action])

    plan.display_plan()

    some_action.display_intent.assert_called_once_with()
    some_other_action.display_intent.assert_called_once_with()


def test_execution_plan__add_actions__display_actions_in_order(mocker):
    some_action_call_time = None
    some_other_action_call_time = None

    def _some_action():
        nonlocal some_action_call_time
        some_action_call_time = datetime.now()

    some_action = mocker.Mock()
    some_action.display_intent.side_effect = _some_action

    def _some_other_action():
        nonlocal some_other_action_call_time
        some_other_action_call_time = datetime.now()

    some_other_action = mocker.Mock()
    some_other_action.display_intent.side_effect = _some_other_action

    plan = execution_plan.ExecutionPlan()
    plan.add_actions([some_action, some_other_action])

    plan.display_plan()

    assert some_other_action_call_time > some_action_call_time


def test_update_config_action__call__updater_called_with_version(mocker):
    mock_updater = mocker.Mock()
    action = execution_plan.update_config_action(mock_updater, sd.SOME_VERSION)

    action()

    mock_updater.assert_called_once_with(sd.SOME_VERSION)


def test_update_config_action__display__message_displayed(
    capture_rich: StringIO, mocker
):
    mock_updater = mocker.Mock()
    action = execution_plan.update_config_action(mock_updater, sd.SOME_VERSION)

    action.display_intent()

    assert "Update version" in capture_rich.getvalue()


def test_update_file_actions__call__updater_called_with_version(mocker):
    perform_change = mocker.patch("hyper_bump_it._files.perform_change")
    some_change = sd.some_planned_change()
    action = execution_plan.update_file_actions([some_change])

    action()

    perform_change.assert_called_once_with(some_change)


def test_update_file_actions__display__message_displayed(capture_rich: StringIO):
    action = execution_plan.update_file_actions([sd.some_planned_change()])

    action.display_intent()

    output = capture_rich.getvalue()
    assert f"????????? {sd.SOME_GLOB_MATCHED_FILE_NAME} ?????????" in output
    assert (
        f"{sd.SOME_FILE_INDEX + 1}: - {sd.SOME_OLD_LINE}\n"
        f"{sd.SOME_FILE_INDEX + 1}: + {sd.SOME_NEW_LINE}" in output
    )


def test_update_file_actions__display_multi_line_change__both_displayed(
    capture_rich: StringIO,
):
    action = execution_plan.update_file_actions(
        [
            sd.some_planned_change(
                line_changes=[
                    sd.some_line_change(),
                    sd.some_line_change(
                        sd.SOME_OTHER_FILE_INDEX,
                        sd.SOME_OTHER_OLD_LINE,
                        sd.SOME_OTHER_NEW_LINE,
                    ),
                ]
            )
        ]
    )

    action.display_intent()

    output = capture_rich.getvalue()
    assert f"????????? {sd.SOME_GLOB_MATCHED_FILE_NAME} ?????????" in output
    assert (
        f"{sd.SOME_FILE_INDEX + 1}: - {sd.SOME_OLD_LINE}\n"
        f"{sd.SOME_FILE_INDEX + 1}: + {sd.SOME_NEW_LINE}\n"
        f"{sd.SOME_OTHER_FILE_INDEX + 1}: - {sd.SOME_OTHER_OLD_LINE}\n"
        f"{sd.SOME_OTHER_FILE_INDEX + 1}: + {sd.SOME_OTHER_NEW_LINE}"
    ) in output


def test_update_file_actions__multi_display__each_name_appears(capture_rich: StringIO):
    action = execution_plan.update_file_actions(
        [
            sd.some_planned_change(),
            sd.some_planned_change(file=Path(sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME)),
        ]
    )

    action.display_intent()

    output = capture_rich.getvalue()
    assert sd.SOME_GLOB_MATCHED_FILE_NAME in output
    assert sd.SOME_OTHER_GLOB_MATCHED_FILE_NAME in output


def test_create_branch_action__call__create_branch_called(mocker):
    mock_create_branch = mocker.patch("hyper_bump_it._git.create_branch")
    mock_repo = mocker.Mock()
    action = execution_plan.CreateBranchAction(mock_repo, sd.SOME_BRANCH)

    action()

    mock_create_branch.assert_called_once_with(mock_repo, sd.SOME_BRANCH)


def test_create_branch_action__display__show_branch_name(
    capture_rich: StringIO, mocker
):
    mock_repo = mocker.Mock()
    action = execution_plan.CreateBranchAction(mock_repo, sd.SOME_BRANCH)

    action.display_intent()

    assert sd.SOME_BRANCH in capture_rich.getvalue()


def test_switch_branch_action__call__switch_to_called(mocker):
    mock_switch_to = mocker.patch("hyper_bump_it._git.switch_to")
    mock_repo = mocker.Mock()
    action = execution_plan.SwitchBranchAction(mock_repo, sd.SOME_BRANCH)

    action()

    mock_switch_to.assert_called_once_with(mock_repo, sd.SOME_BRANCH)


def test_switch_branch_action__display__show_branch_name(
    capture_rich: StringIO, mocker
):
    mock_repo = mocker.Mock()
    action = execution_plan.SwitchBranchAction(mock_repo, sd.SOME_BRANCH)

    action.display_intent()

    assert sd.SOME_BRANCH in capture_rich.getvalue()


def test_commit_changes_action__call__switch_to_called(mocker):
    mock_commit_changes = mocker.patch("hyper_bump_it._git.commit_changes")
    mock_repo = mocker.Mock()
    action = execution_plan.CommitChangesAction(mock_repo, sd.SOME_COMMIT_MESSAGE)

    action()

    mock_commit_changes.assert_called_once_with(mock_repo, sd.SOME_COMMIT_MESSAGE)


def test_commit_changes_action__display__show_commit_message(
    capture_rich: StringIO, mocker
):
    mock_repo = mocker.Mock()
    action = execution_plan.CommitChangesAction(mock_repo, sd.SOME_COMMIT_MESSAGE)

    action.display_intent()

    assert sd.SOME_COMMIT_MESSAGE in capture_rich.getvalue()


def test_create_tag_action__call__switch_to_called(mocker):
    mock_create_tag = mocker.patch("hyper_bump_it._git.create_tag")
    mock_repo = mocker.Mock()
    action = execution_plan.CreateTagAction(mock_repo, sd.SOME_TAG)

    action()

    mock_create_tag.assert_called_once_with(mock_repo, sd.SOME_TAG)


def test_create_tag_action__display__show_tag_name(capture_rich: StringIO, mocker):
    mock_repo = mocker.Mock()
    action = execution_plan.CreateTagAction(mock_repo, sd.SOME_TAG)

    action.display_intent()

    assert sd.SOME_TAG in capture_rich.getvalue()


def test_push_changes_action__call__switch_to_called(mocker):
    mock_push_changes = mocker.patch("hyper_bump_it._git.push_changes")
    mock_repo = mocker.Mock()
    git_operations_info = sd.some_git_operations_info()
    action = execution_plan.PushChangesAction(mock_repo, git_operations_info)

    action()

    mock_push_changes.assert_called_once_with(mock_repo, git_operations_info)


@pytest.mark.parametrize(
    ["actions", "expected_description"],
    [
        (
            sd.some_git_actions(
                commit=GitAction.CreateAndPush,
                branch=GitAction.Skip,
                tag=GitAction.Skip,
            ),
            f"Push commit to {sd.SOME_REMOTE}",
        ),
        (
            # create tag, but only push commit
            sd.some_git_actions(
                commit=GitAction.CreateAndPush,
                branch=GitAction.Skip,
                tag=GitAction.Create,
            ),
            f"Push commit to {sd.SOME_REMOTE}",
        ),
        (
            sd.some_git_actions(
                commit=GitAction.CreateAndPush,
                branch=GitAction.CreateAndPush,
                tag=GitAction.Skip,
            ),
            f"Push commit to {sd.SOME_REMOTE} on branch {sd.SOME_BRANCH}",
        ),
        (
            sd.some_git_actions(
                commit=GitAction.CreateAndPush,
                branch=GitAction.Skip,
                tag=GitAction.CreateAndPush,
            ),
            f"Push commit to {sd.SOME_REMOTE} with tag {sd.SOME_TAG}",
        ),
        (
            sd.some_git_actions(
                commit=GitAction.CreateAndPush,
                branch=GitAction.CreateAndPush,
                tag=GitAction.CreateAndPush,
            ),
            f"Push commit to {sd.SOME_REMOTE} on branch {sd.SOME_BRANCH} with tag {sd.SOME_TAG}",
        ),
    ],
)
def test_push_changes__display__show_description(
    actions, expected_description, capture_rich: StringIO, mocker
):
    mock_repo = mocker.Mock()
    action = execution_plan.PushChangesAction(
        mock_repo, sd.some_git_operations_info(actions=actions)
    )

    action.display_intent()

    assert expected_description in capture_rich.getvalue()


@pytest.mark.parametrize(
    ["actions", "expected_initial_actions", "expected_final_actions"],
    [
        (
            sd.some_git_actions(
                commit=GitAction.Skip, branch=GitAction.Skip, tag=GitAction.Skip
            ),
            [],
            [],
        ),
        (
            sd.some_git_actions(
                commit=GitAction.Create, branch=GitAction.Skip, tag=GitAction.Skip
            ),
            [],
            [execution_plan.CommitChangesAction],
        ),
        (
            sd.some_git_actions(
                commit=GitAction.Create, branch=GitAction.Skip, tag=GitAction.Create
            ),
            [],
            [execution_plan.CommitChangesAction, execution_plan.CreateTagAction],
        ),
        (
            sd.some_git_actions(
                commit=GitAction.Create, branch=GitAction.Create, tag=GitAction.Skip
            ),
            [execution_plan.CreateBranchAction, execution_plan.SwitchBranchAction],
            [execution_plan.CommitChangesAction, execution_plan.SwitchBranchAction],
        ),
        (
            sd.some_git_actions(
                commit=GitAction.Create, branch=GitAction.Create, tag=GitAction.Create
            ),
            [execution_plan.CreateBranchAction, execution_plan.SwitchBranchAction],
            [
                execution_plan.CommitChangesAction,
                execution_plan.CreateTagAction,
                execution_plan.SwitchBranchAction,
            ],
        ),
        (
            sd.some_git_actions(
                commit=GitAction.CreateAndPush,
                branch=GitAction.Skip,
                tag=GitAction.Skip,
            ),
            [],
            [execution_plan.CommitChangesAction, execution_plan.PushChangesAction],
        ),
    ],
)
def test_git_actions__some_git_actions__expected_action_lists(
    actions,
    expected_initial_actions: list[Type],
    expected_final_actions: list[Type],
    mocker,
):
    initial_actions, final_actions = execution_plan.git_actions(
        sd.some_git_operations_info(actions=actions), repo=mocker.Mock()
    )

    for action, expected_type in zip_longest(initial_actions, expected_initial_actions):
        assert isinstance(action, expected_type)

    for action, expected_type in zip_longest(final_actions, expected_final_actions):
        assert isinstance(action, expected_type)
