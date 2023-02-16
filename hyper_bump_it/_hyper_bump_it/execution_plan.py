"""
Structured plan of what operations will be performed.

The plan is created before performing any operations so that the user can confirm the changes
to be made before files are edited.
"""
from typing import Optional, Protocol, TypeVar

from git import Repo
from rich.text import Text

from . import files, ui, vcs
from .compat import LiteralString
from .config import ConfigVersionUpdater, GitAction
from .planned_changes import PlannedChange
from .version import Version


class Action(Protocol):
    def __call__(self) -> None:
        """
        Perform the operation represented by this action.
        """

    def display_intent(self) -> None:
        """
        Display a description of the operation that would occur when this action is executed.
        """


TAction = TypeVar("TAction", bound=Action)


class ActionGroup:
    def __init__(
        self,
        intent_description: LiteralString,
        execution_description: LiteralString,
        actions: list[TAction],
    ) -> None:
        """
        Initialize an instance.

        :param intent_description: Text displayed when displaying the intended plan.
        :param execution_description: Text displayed before executing the actions.
        :param actions: Sub-actions contained by this group.
        """
        self._intent_description: LiteralString = intent_description
        self._description: LiteralString = execution_description
        self._actions = actions

    def __call__(self) -> None:
        ui.display(self._description)
        for action in self._actions:
            action()

    def display_intent(self) -> None:
        ui.display(self._intent_description)
        for action in self._actions:
            action.display_intent()


class ExecutionPlan:
    def __init__(self) -> None:
        self._actions: list[Action] = []

    def add_action(self, action: Action) -> None:
        self._actions.append(action)

    def add_actions(self, actions: list[Action]) -> None:
        self._actions.extend(actions)

    def execute_plan(self) -> None:
        for action in self._actions:
            action()

    def display_plan(self, show_header: bool = True) -> None:
        if show_header:
            ui.display("[bold]Execution Plan[/]:")
        for action in self._actions:
            action.display_intent()


class UpdateConfiAction:
    def __init__(self, updater: ConfigVersionUpdater, new_version: Version) -> None:
        self._updater = updater
        self._new_version = new_version

    def __call__(self) -> None:
        ui.display("Updating version in configuration file")
        files.perform_change(self._updater(self._new_version))

    def display_intent(self) -> None:
        ui.display("Update version in configuration file")


def update_config_action(updater: ConfigVersionUpdater, new_version: Version) -> Action:
    return UpdateConfiAction(updater, new_version)


class ChangeFileAction:
    def __init__(self, change: PlannedChange) -> None:
        self._change = change

    def __call__(self) -> None:
        message = Text("Updating ")
        message.append(str(self._change.relative_file), style="file.path")
        ui.display(message)
        files.perform_change(self._change)

    def display_intent(self) -> None:
        ui.rule(Text(str(self._change.relative_file), style="file.path"))
        ui.display_diff(self._change.change_diff)


def update_file_actions(planned_changes: list[PlannedChange]) -> Action:
    return ActionGroup(
        intent_description="Update files",
        execution_description="Updating files",
        actions=[ChangeFileAction(change) for change in planned_changes],
    )


class DisplayFilePatchesAction:
    def __init__(self, changes: list[PlannedChange]) -> None:
        self._changes = changes

    def __call__(self) -> None:
        raise ValueError("This action should only every be used to display an intent")

    def display_intent(self) -> None:
        for change in self._changes:
            ui.display_diff(change.change_diff)


class CreateBranchAction:
    def __init__(self, repo: Repo, branch_name: str) -> None:
        self._repo = repo
        self._branch_name = branch_name

    def __call__(self) -> None:
        ui.display(
            Text("Creating branch ").append(self._branch_name, style="vcs.branch")
        )
        vcs.create_branch(self._repo, self._branch_name)

    def display_intent(self) -> None:
        ui.display(Text("Create branch ").append(self._branch_name, style="vcs.branch"))


class SwitchBranchAction:
    def __init__(self, repo: Repo, branch_name: str) -> None:
        self._repo = repo
        self._branch_name = branch_name

    def __call__(self) -> None:
        ui.display(
            Text("Switching to branch ").append(self._branch_name, style="vcs.branch")
        )
        vcs.switch_to(self._repo, self._branch_name)

    def display_intent(self) -> None:
        ui.display(
            Text("Switch to branch ").append(self._branch_name, style="vcs.branch")
        )


class CommitChangesAction:
    def __init__(self, repo: Repo, commit_message: str) -> None:
        self._repo = repo
        self._commit_message = commit_message

    def __call__(self) -> None:
        ui.display(
            Text("Committing changes: ").append(
                self._commit_message, style="vcs.commit"
            )
        )
        vcs.commit_changes(self._repo, self._commit_message)

    def display_intent(self) -> None:
        ui.display(
            Text("Commit changes: ").append(self._commit_message, style="vcs.commit")
        )


class CreateTagAction:
    def __init__(self, repo: Repo, tag_name: str) -> None:
        self._repo = repo
        self._tag_name = tag_name

    def __call__(self) -> None:
        ui.display(Text("Tagging commit: ").append(self._tag_name, style="vcs.tag"))
        vcs.create_tag(self._repo, self._tag_name)

    def display_intent(self) -> None:
        ui.display(Text("Tag commit: ").append(self._tag_name, style="vcs.tag"))


class PushChangesAction:
    def __init__(self, repo: Repo, operation_info: vcs.GitOperationsInfo) -> None:
        self._repo = repo
        self._operation_info = operation_info

    def __call__(self) -> None:
        ui.display(self._description(intent=False))
        vcs.push_changes(self._repo, self._operation_info)

    def display_intent(self) -> None:
        ui.display(self._description(intent=True))

    def _description(self, intent: bool) -> Text:
        message = Text("Push" if intent else "Pushing")
        message.append(" commit to ")
        message.append(self._operation_info.remote, style="vcs.remote")
        if self._operation_info.actions.branch == GitAction.CreateAndPush:
            message.append(" on branch ")
            message.append(self._operation_info.branch_name, style="vcs.branch")
        if self._operation_info.actions.tag == GitAction.CreateAndPush:
            message.append(" with tag ")
            message.append(self._operation_info.tag_name, style="vcs.tag")
        return message


def git_actions(
    git_operations_info: vcs.GitOperationsInfo, repo: Repo
) -> tuple[list[Action], list[Action]]:
    initial_actions: list[Action] = []
    final_actions: list[Action] = []
    switch_back: Optional[Action] = None
    if git_operations_info.actions.branch.should_create:
        initial_actions.append(
            CreateBranchAction(repo, git_operations_info.branch_name)
        )
        initial_actions.append(
            SwitchBranchAction(repo, git_operations_info.branch_name)
        )
        switch_back = SwitchBranchAction(repo, repo.active_branch.name)

    if git_operations_info.actions.commit.should_create:
        final_actions.append(
            CommitChangesAction(repo, git_operations_info.commit_message)
        )
    if git_operations_info.actions.tag.should_create:
        final_actions.append(CreateTagAction(repo, git_operations_info.tag_name))
    if git_operations_info.actions.any_push:
        final_actions.append(PushChangesAction(repo, git_operations_info))

    if switch_back is not None:
        final_actions.append(switch_back)
    return initial_actions, final_actions
