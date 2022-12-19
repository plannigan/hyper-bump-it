from typing import Optional

from rich import print, prompt
from semantic_version import Version

from hyper_bump_it import _execution_plan as execution_plan
from hyper_bump_it import _files as files
from hyper_bump_it import _git as git
from hyper_bump_it._config import Config, ConfigVersionUpdater
from hyper_bump_it._files import PlannedChange
from hyper_bump_it._text_formatter import TextFormatter


def do_bump(config: Config) -> None:
    text_formatter = TextFormatter(config.current_version, config.new_version)
    planned_changes: list[PlannedChange] = []
    for file in config.files:
        planned_changes.extend(
            files.collect_planned_changes(config.project_root, file, text_formatter)
        )
    git_operations_info = git.GitOperationsInfo.from_config(config.git, text_formatter)
    if git_operations_info.actions.all_skip:
        git_repo = None
    else:
        git_repo = git.get_vetted_repo(config.project_root, git_operations_info)

    plan = _construct_plan(
        config.new_version,
        planned_changes,
        git_operations_info,
        git_repo,
        config.config_version_updater,
    )
    plan.display_plan()
    if config.dry_run:
        return

    print()  # blank line before prompt
    if config.show_confirm_prompt:
        response = prompt.Confirm.ask(
            "Do you want to perform these actions?", default=False
        )

        if not response:
            return

    plan.execute_plan()


def _construct_plan(
    new_version: Version,
    planned_changes: list[PlannedChange],
    git_operations_info: git.GitOperationsInfo,
    repo: Optional[git.Repo],
    config_version_updater: Optional[ConfigVersionUpdater],
) -> execution_plan.ExecutionPlan:
    plan = execution_plan.ExecutionPlan()
    git_actions: list[execution_plan.Action] = []
    if repo is not None:
        initial_git_actions, git_actions = execution_plan.git_actions(
            git_operations_info, repo
        )
        plan.add_actions(initial_git_actions)
    if config_version_updater is not None:
        plan.add_action(
            execution_plan.update_config_action(config_version_updater, new_version)
        )
    plan.add_action(execution_plan.update_file_actions(planned_changes))
    plan.add_actions(git_actions)
    return plan
