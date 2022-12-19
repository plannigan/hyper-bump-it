"""
Structured plan of what operations will be performed.

The plan is created before performing any operations so that the user can confirm the changes
to be made before files are edited.
"""
from typing import Optional, Protocol, TypeVar

from rich import print
from rich.rule import Rule
from semantic_version import Version

from hyper_bump_it import _files as files
from hyper_bump_it import _git as git
from hyper_bump_it._config import ConfigVersionUpdater, GitAction


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
        intent_description: str,
        execution_description: str,
        actions: list[TAction],
    ) -> None:
        """
        Initialize an instance.

        :param intent_description: Text displayed when displaying the intended plan.
        :param execution_description: Text displayed before executing the actions.
        :param actions: Sub-actions contained by this group.
        """
        self._intent_description = intent_description
        self._description = execution_description
        self._actions = actions

    def __call__(self) -> None:
        print(self._description)
        for action in self._actions:
            action()

    def display_intent(self) -> None:
        print(self._intent_description)
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

    def display_plan(self) -> None:
        print("[bold]Execution Plan[/]:")
        for action in self._actions:
            action.display_intent()


class UpdateConfiAction:
    def __init__(self, updater: ConfigVersionUpdater, new_version: Version) -> None:
        self._updater = updater
        self._new_version = new_version

    def __call__(self) -> None:
        print("Updating version in configuration file")
        self._updater(self._new_version)

    def display_intent(self) -> None:
        print("Update version in configuration file")


def update_config_action(updater: ConfigVersionUpdater, new_version: Version) -> Action:
    return UpdateConfiAction(updater, new_version)


class ChangeFileAction:
    def __init__(self, change: files.PlannedChange) -> None:
        self._change = change

    def __call__(self) -> None:
        print(f"Updating {self._change.file}")
        files.perform_change(self._change)

    def display_intent(self) -> None:
        print(Rule(title=str(self._change.file)))
        for line_change in self._change.line_changes:
            print(f"{line_change.line_index + 1}: [red]- {line_change.old_line}")
            print(
                f"{line_change.line_index + 1}: [green]+ {line_change.new_line.strip()}"
            )


def update_file_actions(planned_changes: list[files.PlannedChange]) -> Action:
    return ActionGroup(
        intent_description="Update files",
        execution_description="Updating files",
        actions=[ChangeFileAction(change) for change in planned_changes],
    )


class CreateBranchAction:
    def __init__(self, repo: git.Repo, branch_name: str) -> None:
        self._repo = repo
        self._branch_name = branch_name

    def __call__(self) -> None:
        print(f"Creating branch {self._branch_name}")
        git.create_branch(self._repo, self._branch_name)

    def display_intent(self) -> None:
        print(f"Create branch {self._branch_name}")


class SwitchBranchAction:
    def __init__(self, repo: git.Repo, branch_name: str) -> None:
        self._repo = repo
        self._branch_name = branch_name

    def __call__(self) -> None:
        print(f"Switching to branch {self._branch_name}")
        git.switch_to(self._repo, self._branch_name)

    def display_intent(self) -> None:
        print(f"Switch to branch {self._branch_name}")


class CommitChangesAction:
    def __init__(self, repo: git.Repo, commit_message: str) -> None:
        self._repo = repo
        self._commit_message = commit_message

    def __call__(self) -> None:
        print(f"Committing changes: {self._commit_message}")
        git.commit_changes(self._repo, self._commit_message)

    def display_intent(self) -> None:
        print(f"Commit changes: {self._commit_message}")


class CreateTagAction:
    def __init__(self, repo: git.Repo, tag_name: str) -> None:
        self._repo = repo
        self._tag_name = tag_name

    def __call__(self) -> None:
        print(f"Tagging commit: {self._tag_name}")
        git.create_tag(self._repo, self._tag_name)

    def display_intent(self) -> None:
        print(f"Tag commit: {self._tag_name}")


class PushChangesAction:
    def __init__(self, repo: git.Repo, operation_info: git.GitOperationsInfo) -> None:
        self._repo = repo
        self._operation_info = operation_info

    def __call__(self) -> None:
        print(self._description(intent=False))
        git.push_changes(self._repo, self._operation_info)

    def display_intent(self) -> None:
        print(self._description(intent=True))

    def _description(self, intent: bool) -> str:
        action = "Push" if intent else "Pushing"
        message = f"{action} commit to {self._operation_info.remote}"
        if self._operation_info.actions.branch == GitAction.CreateAndPush:
            message = f"{message} on branch {self._operation_info.branch_name}"
        if self._operation_info.actions.tag == GitAction.CreateAndPush:
            message = f"{message} with tag {self._operation_info.tag_name}"
        return message


def git_actions(
    git_operations_info: git.GitOperationsInfo, repo: git.Repo
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
