"""
Program configuration
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from semantic_version import Version

from hyper_bump_it._config.core import GitAction
from hyper_bump_it._config.file import ConfigVersionUpdater


@dataclass
class GitActions:
    commit: GitAction
    branch: GitAction
    tag: GitAction

    def __post_init__(self) -> None:
        if not self.commit.should_create:
            if self.branch.should_create:
                raise ValueError("if 'commit' is Skip, 'branch' must also be Skip")
            if self.tag.should_create:
                raise ValueError("if 'commit' is Skip, 'tag' must also be Skip")

    @property
    def any_push(self) -> bool:
        return any(
            action == GitAction.CreateAndPush
            for action in (self.commit, self.branch, self.tag)
        )


@dataclass
class Git:
    remote: str
    commit_format_pattern: str
    branch_format_pattern: str
    tag_format_pattern: str
    actions: GitActions


@dataclass
class File:
    file_glob: str
    search_format_pattern: str
    replace_format_pattern: str


@dataclass
class Config:
    current_version: Version
    new_version: Version
    project_root: Path
    files: list[File]
    git: Git
    config_version_updater: Optional[ConfigVersionUpdater]
