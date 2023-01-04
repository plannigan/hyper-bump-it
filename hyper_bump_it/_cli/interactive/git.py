"""
Go through a series of prompts to construct a custom Git integration configuration.
"""
from enum import Enum
from typing import Optional, TypeVar

from pydantic import ValidationError
from rich import print, prompt

from hyper_bump_it._cli.interactive.prompt import enum_prompt
from hyper_bump_it._config import (
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
from hyper_bump_it._error import first_error_message


class GitMenu(Enum):
    Remote = "remote"
    CommitFormatPattern = "commit"
    BranchFormatPattern = "branch"
    TagFormatPattern = "tag"
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

    def _configure_format_pattern(
        self, name: str, config_name: str, current_pattern: str, default: str
    ) -> None:
        self._store_update(
            config_name, _prompt_format_pattern(name, current_pattern, default)
        )

    def _store_update(self, config_name: str, value: Optional[str]) -> None:
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
