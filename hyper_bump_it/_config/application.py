"""
Program configuration
"""
from dataclasses import astuple, dataclass
from pathlib import Path
from typing import Callable, Optional, Union, cast

from semantic_version import Version

from hyper_bump_it._config import file, keystone_parser
from hyper_bump_it._config.cli import BumpByArgs, BumpPart, BumpToArgs
from hyper_bump_it._config.core import GitAction, validate_git_action_combination
from hyper_bump_it._error import KeystoneFileGlobError


@dataclass
class GitActions:
    commit: GitAction
    branch: GitAction
    tag: GitAction

    def __post_init__(self) -> None:
        validate_git_action_combination(
            commit=self.commit, branch=self.branch, tag=self.tag
        )

    @property
    def any_push(self) -> bool:
        return any(action == GitAction.CreateAndPush for action in astuple(self))

    @property
    def all_skip(self) -> bool:
        return all(action == GitAction.Skip for action in astuple(self))


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
    dry_run: bool
    show_confirm_prompt: bool
    config_version_updater: Optional[file.ConfigVersionUpdater]


BUMP_FUNCTIONS: dict[BumpPart, Callable[[Version], Version]] = {
    BumpPart.Major: Version.next_major,
    BumpPart.Minor: Version.next_minor,
    BumpPart.Patch: Version.next_patch,
}


def config_for_bump_to(args: BumpToArgs) -> Config:
    """
    Produce an application configuration.

    :param args: Arguments passed to command line command.
    :return: Configuration for how the application should execute.
    :raises ConfigurationError: No file was found or there was some error in the file.
    :raises FormatError: Search pattern for keystone file could not be converted.
    :raises KeystoneError: Keystone configuration could not produce the current version.
    """
    file_config, version_updater = file.read_config(args.config_file, args.project_root)

    return Config(
        current_version=_current_version(
            args.current_version, file_config, args.project_root
        ),
        new_version=args.new_version,
        project_root=args.project_root,
        files=_convert_files(file_config.files),
        git=_convert_git(args, file_config.git),
        dry_run=args.dry_run,
        show_confirm_prompt=_show_confirm_prompt(
            file_config.show_confirm_prompt, args.skip_confirm_prompt
        ),
        config_version_updater=version_updater,
    )


def config_for_bump_by(args: BumpByArgs) -> Config:
    """
    Produce an application configuration.

    :param args: Arguments passed to command line command.
    :return: Configuration for how the application should execute.
    :raises ConfigurationError: No file was found or there was some error in the file.
    :raises FormatError: Search pattern for keystone file could not be converted.
    :raises KeystoneError: Keystone configuration could not produce the current version.
    """
    file_config, version_updater = file.read_config(args.config_file, args.project_root)
    current_version = _current_version(
        args.current_version, file_config, args.project_root
    )

    return Config(
        current_version=current_version,
        new_version=BUMP_FUNCTIONS[args.part_to_bump](current_version),
        project_root=args.project_root,
        files=_convert_files(file_config.files),
        git=_convert_git(args, file_config.git),
        dry_run=args.dry_run,
        show_confirm_prompt=_show_confirm_prompt(
            file_config.show_confirm_prompt, args.skip_confirm_prompt
        ),
        config_version_updater=version_updater,
    )


def _current_version(
    args_version: Version, file_config: file.ConfigFile, project_root: Path
) -> Version:
    if args_version is not None:
        return args_version

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


def _convert_git(args: Union[BumpToArgs, BumpByArgs], git: file.Git) -> Git:
    return Git(
        remote=args.remote or git.remote,
        commit_format_pattern=args.commit_format_pattern or git.commit_format_pattern,
        branch_format_pattern=args.branch_format_pattern or git.branch_format_pattern,
        tag_format_pattern=args.tag_format_pattern or git.tag_format_pattern,
        actions=GitActions(
            commit=args.commit or git.actions.commit,
            branch=args.branch or git.actions.branch,
            tag=args.tag or git.actions.tag,
        ),
    )


def _show_confirm_prompt(
    file_show_confirm: bool, cli_skip_confirm_prompt: Optional[bool]
) -> bool:
    return (
        file_show_confirm
        if cli_skip_confirm_prompt is None
        else not cli_skip_confirm_prompt
    )
