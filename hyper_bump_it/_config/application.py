"""
Program configuration
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, cast

from semantic_version import Version

from hyper_bump_it._config import file, keystone_parser
from hyper_bump_it._config.core import GitAction
from hyper_bump_it._error import KeystoneFileGlobError


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
    config_version_updater: Optional[file.ConfigVersionUpdater]


def config_from_file(
    new_version: Version, config_file: Optional[Path], project_root: Path
) -> Config:
    """
    Produce an application configuration.

    :param new_version: New version that will be used for the update operations.
    :param config_file: Dedicated config file to read from instead of doing config file discovery.
    :param project_root: Directory to look for a configuration file.
    :return: Configuration for how the application should execute.
    :raises ConfigurationError: No file was found or there was some error in the file.
    :raises FormatError: Search pattern for keystone file could not be converted.
    :raises KeystoneError: Keystone configuration could not produce the current version.
    """
    file_config, version_updater = file.read_config(config_file, project_root)

    return Config(
        current_version=_current_version(file_config, project_root),
        new_version=new_version,
        project_root=project_root,
        files=_convert_files(file_config.files),
        git=_convert_git(file_config.git),
        config_version_updater=version_updater,
    )


def _current_version(file_config: file.ConfigFile, project_root: Path) -> Version:
    if file_config.current_version is not None:
        return file_config.current_version

    # Validator ensures that a keystone config will exist if there is no current version
    file_glob, search_format_pattern = cast(
        tuple[str, str], file_config.keystone_config
    )

    matched_files = list(project_root.glob(file_glob))
    if len(matched_files) != 1:
        raise KeystoneFileGlobError(file_glob, matched_files)

    return keystone_parser.find_current_version(matched_files[0], search_format_pattern)


def _convert_files(config_files: list[file.File]) -> list[File]:
    return [
        File(
            file_glob=f.file_glob,
            search_format_pattern=f.search_format_pattern,
            replace_format_pattern=f.replace_format_pattern or f.search_format_pattern,
        )
        for f in config_files
    ]


def _convert_git(git: file.Git) -> Git:
    return Git(
        remote=git.remote,
        commit_format_pattern=git.commit_format_pattern,
        branch_format_pattern=git.branch_format_pattern,
        tag_format_pattern=git.tag_format_pattern,
        actions=GitActions(
            commit=git.actions.commit,
            branch=git.actions.branch,
            tag=git.actions.tag,
        ),
    )
