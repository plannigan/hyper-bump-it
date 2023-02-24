from typing import Optional

from git import Repo

from . import execution_plan, files, ui, vcs
from .config import Config, ConfigVersionUpdater
from .format_pattern import TextFormatter
from .planned_changes import PlannedChange
from .vcs import GitOperationsInfo
from .version import Version


def do_bump(config: Config) -> None:
    text_formatter = TextFormatter(config.current_version, config.new_version)
    planned_changes: list[PlannedChange] = []
    for file in config.files:
        planned_changes.extend(
            files.collect_planned_changes(config.project_root, file, text_formatter)
        )
    git_operations_info = GitOperationsInfo.from_config(config.git, text_formatter)
    if git_operations_info.actions.all_skip:
        git_repo = None
    else:
        git_repo = vcs.get_vetted_repo(config.project_root, git_operations_info)

    if config.patch:
        plan = _construct_patch_plan(
            config.new_version,
            planned_changes,
            config.config_version_updater,
        )
    else:
        plan = _construct_plan(
            config.new_version,
            planned_changes,
            git_operations_info,
            git_repo,
            config.config_version_updater,
        )
    plan.display_plan(show_header=not config.patch)
    if config.no_execute_plan:
        return

    ui.blank_line()
    if config.show_confirm_prompt:
        response = ui.confirm("Do you want to perform these actions?", default=False)

        if not response:
            return

    plan.execute_plan()


def _construct_plan(
    new_version: Version,
    planned_changes: list[PlannedChange],
    git_operations_info: GitOperationsInfo,
    repo: Optional[Repo],
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


def _construct_patch_plan(
    new_version: Version,
    planned_changes: list[PlannedChange],
    config_version_updater: Optional[ConfigVersionUpdater],
) -> execution_plan.ExecutionPlan:
    plan = execution_plan.ExecutionPlan()
    if config_version_updater is not None:
        planned_changes.append(config_version_updater(new_version))
    plan.add_action(execution_plan.DisplayFilePatchesAction(planned_changes))
    return plan
