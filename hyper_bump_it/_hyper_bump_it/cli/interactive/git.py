"""
Go through a series of prompts to construct a custom Git integration configuration.
"""
from enum import Enum
from typing import Optional, TypeVar, Union

from pydantic import ValidationError
from rich import print, prompt

from ...config import (
    DEFAULT_BRANCH_ACTION,
    DEFAULT_BRANCH_FORMAT_PATTERN,
    DEFAULT_COMMIT_ACTION,
    DEFAULT_COMMIT_FORMAT_PATTERN,
    DEFAULT_REMOTE,
    DEFAULT_TAG_ACTION,
    DEFAULT_TAG_FORMAT_PATTERN,
    GitAction,
    GitActionsConfigFile,
    GitConfigFile,
)
from ...config.core import DEFAULT_ALLOWED_INITIAL_BRANCHES
from ...error import first_error_message
from .prompt import enum_prompt


class GitMenu(Enum):
    Remote = "remote"
    CommitFormatPattern = "commit"
    BranchFormatPattern = "branch"
    TagFormatPattern = "tag"
    AllowedBranches = "allowed-branches"
    Actions = "actions"
    Done = "done"


class GitConfigEditor:
    def __init__(self, initial_config: GitConfigFile) -> None:
        self._config: GitConfigFile = initial_config.copy(deep=True)
        self._config_funcs = {
            GitMenu.Remote: self._configure_remote,
            GitMenu.CommitFormatPattern: self._configure_commit_format_pattern,
            GitMenu.BranchFormatPattern: self._configure_branch_format_pattern,
            GitMenu.TagFormatPattern: self._configure_tag_format_pattern,
            GitMenu.AllowedBranches: self._configure_allowed_branches,
            GitMenu.Actions: self._configure_actions,
        }

    def configure(self) -> GitConfigFile:
        """
        Use interactive prompts to allow the user to edit the configuration.

        :return: Configuration with the user's edits.
        """
        while (selection := _prompt_git_menu()) is not GitMenu.Done:
            self._config_funcs[selection]()

        return self._config

    def _configure_remote(self) -> None:
        self._store_update("remote", _prompt_remote(self._config.remote))

    def _configure_commit_format_pattern(self) -> None:
        self._configure_format_pattern(
            "commit message",
            "commit_format_pattern",
            self._config.commit_format_pattern,
            DEFAULT_COMMIT_FORMAT_PATTERN,
        )

    def _configure_branch_format_pattern(self) -> None:
        self._configure_format_pattern(
            "branch name",
            "branch_format_pattern",
            self._config.branch_format_pattern,
            DEFAULT_BRANCH_FORMAT_PATTERN,
        )

    def _configure_tag_format_pattern(self) -> None:
        self._configure_format_pattern(
            "tag name",
            "tag_format_pattern",
            self._config.tag_format_pattern,
            DEFAULT_TAG_FORMAT_PATTERN,
        )

    def _configure_allowed_branches(self) -> None:
        allowed_branches, extend_overload_branches = AllowedBranchEditor(
            self._config.allowed_initial_branches
        ).configure()
        self._config = self._config.copy(
            update={
                "allowed_initial_branches": allowed_branches,
                "extend_allowed_initial_branches": extend_overload_branches,
            }
        )

    def _configure_format_pattern(
        self, name: str, config_name: str, current_pattern: str, default: str
    ) -> None:
        self._store_update(
            config_name, _prompt_format_pattern(name, current_pattern, default)
        )

    def _store_update(
        self, config_name: str, value: Union[Optional[str], frozenset[str]]
    ) -> None:
        if value is not None:
            self._config = self._config.copy(update={config_name: value})

    def _configure_actions(self) -> None:
        print("There are three Git actions: create, branch, tag")
        print(
            "They can each be set to: "
            f"{GitAction.Skip.value}, {GitAction.Create.value}, {GitAction.CreateAndPush.value}"
        )
        print(
            "However, some combinations are not valid. If an invalid combination is detected,"
            " an error message will be displayed before requesting new values for each action."
        )
        while True:
            updated_commit = _prompt_action(
                "commit", self._config.actions.commit, DEFAULT_COMMIT_ACTION
            )
            updated_branch = _prompt_action(
                "branch", self._config.actions.branch, DEFAULT_BRANCH_ACTION
            )
            updated_tag = _prompt_action(
                "tag", self._config.actions.tag, DEFAULT_TAG_ACTION
            )
            try:
                actions = GitActionsConfigFile(
                    commit=updated_commit, branch=updated_branch, tag=updated_tag
                )
                break
            except ValidationError as ex:
                print(f"[prompt.invalid]Error[/]: {first_error_message(ex)}")

        self._config = self._config.copy(update={"actions": actions})


def _prompt_git_menu() -> GitMenu:
    return enum_prompt(
        "What part of configuration would you like to edit?",
        option_descriptions={
            GitMenu.Remote: "Name of remote to use when pushing changes",
            GitMenu.CommitFormatPattern: "Format pattern to use for commit message",
            GitMenu.BranchFormatPattern: "Format pattern to use for branch name",
            GitMenu.TagFormatPattern: "Format pattern to use for tag name",
            GitMenu.AllowedBranches: "Names of allowed initial branches",
            GitMenu.Actions: "Configure what Git actions should be performed",
            GitMenu.Done: "Stop editing the Git integration settings",
        },
        default=GitMenu.Done,
    )


def _prompt_remote(current_remote: str) -> Optional[str]:
    return prompt.Prompt.ask(
        f"When an action is set to 'create-and-push`, the name of the remote repository is needed."
        f"The remote is currently set to: "
        f"[bold]{current_remote}[/]{_default_message(current_remote, DEFAULT_REMOTE)}\n"
        "Enter a new name or leave it blank to keep the value",
        show_default=False,
        default=None,
    )


def _prompt_format_pattern(
    name: str, current_pattern: str, default: str
) -> Optional[str]:
    return prompt.Prompt.ask(
        f"Format patterns are used to generate text. "
        f"The format pattern for {name} is currently set to: "
        f"[bold]{current_pattern}[/]{_default_message(current_pattern, default)}\n"
        "Enter a new format pattern or leave it blank to keep the value",
        show_default=False,
        default=None,
    )


def _prompt_action(
    name: str, current_value: GitAction, default: GitAction
) -> GitAction:
    selection = prompt.Prompt.ask(
        f"The {name} action is currently set to: "
        f"[bold]{current_value.value}[/]{_default_message(current_value, default)}\n"
        "Enter a new value or leave it blank to keep the value",
        choices=[option.value for option in GitAction],
        show_default=False,
        default=None,
    )
    if selection is None:
        return current_value
    return GitAction(selection)


T = TypeVar("T")


def _default_message(current_value: T, default: T) -> str:
    return " [prompt.default](the default)[/]" if current_value == default else ""


class AllowedBranchesMenu(Enum):
    Add = "add"
    Remove = "remove"
    Clear = "clear"
    Done = "done"


class AllowedBranchEditor:
    def __init__(self, initial_config: frozenset[str]) -> None:
        self._config = initial_config
        self._config_funcs = {
            AllowedBranchesMenu.Add: self._configure_add,
            AllowedBranchesMenu.Remove: self._configure_remove,
            AllowedBranchesMenu.Clear: self._configure_clear,
        }

    def configure(self) -> tuple[frozenset[str], frozenset[str]]:
        """
        Use interactive prompts to allow the user to edit the configuration.

        :return: Configuration with the user's edits.
        """
        while (
            selection := _prompt_allowed_branches_menu(self._config)
        ) is not AllowedBranchesMenu.Done:
            self._config_funcs[selection]()

        return self._partition_config()

    def _configure_add(self) -> None:
        result = _prompt_add_branch()
        if result is None:
            print("No name entered. Nothing will be added.")
        else:
            self._config |= {result}

    def _configure_remove(self) -> None:
        if len(self._config) == 0:
            print("There are no branches to remove.")
        elif len(self._config) == 1:
            self._configure_clear()
        else:
            self._config -= {_prompt_select_branch(self._config)}

    def _configure_clear(self) -> None:
        self._config = frozenset()

    def _partition_config(self) -> tuple[frozenset[str], frozenset[str]]:
        # from the interactive menu, we will assume that users want to use extend the default branches are present.
        if DEFAULT_ALLOWED_INITIAL_BRANCHES.issubset(self._config):
            return (
                DEFAULT_ALLOWED_INITIAL_BRANCHES,
                self._config - DEFAULT_ALLOWED_INITIAL_BRANCHES,
            )

        return self._config, frozenset()


def _prompt_allowed_branches_menu(config: frozenset[str]) -> AllowedBranchesMenu:
    print(
        "When one or more branch names are configured, execution is only allowed from one of the listed names."
    )
    print("When not branch names are configured, execution is allowed from any branch.")
    _display_branch_list(config)
    return enum_prompt(
        "What change would you like to make?",
        option_descriptions={
            AllowedBranchesMenu.Add: "Add a branch name to the allowed branches",
            AllowedBranchesMenu.Remove: "Remove a branch name from the allowed branches",
            AllowedBranchesMenu.Clear: "Remove all of the branch names",
            AllowedBranchesMenu.Done: "Stop editing the allowed branches setting",
        },
        default=AllowedBranchesMenu.Done,
    )


def _display_branch_list(config: frozenset[str]) -> None:
    if len(config) == 0:
        print("No allowed branches are currently set.")
    elif len(config) == 1:
        branch = next(iter(config))
        print(f"The allowed branch is '{branch}'.")
    else:
        branches = "', '".join(config)
        print(f"The allowed branches are: '{branches}'")


def _prompt_add_branch() -> Optional[str]:
    return prompt.Prompt.ask(
        "Enter the name of the branch that will be allowed as the initial branch when executing.",
        show_default=False,
        default=None,
    )


def _prompt_select_branch(allowed_branches: frozenset[str]) -> str:
    return prompt.Prompt.ask(
        "Enter the name of the branch to remove.",
        show_default=False,
        choices=list(allowed_branches),
        show_choices=False,
    )
