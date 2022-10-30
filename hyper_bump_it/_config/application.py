"""
Program configuration
"""
from dataclasses import dataclass, field
from enum import Enum, auto

from hyper_bump_it._text_formatter import keys

DEFAULT_REMOTE = "origin"
DEFAULT_COMMIT_PATTERN = (
    f"Bump version: {{{keys.CURRENT_VERSION}}} → {{{keys.NEW_VERSION}}}"
)
DEFAULT_BRANCH_PATTERN = f"bump_version_to_{{{keys.NEW_VERSION}}}"
DEFAULT_TAG_PATTERN = f"v{{{keys.NEW_VERSION}}}"


class GitAction(Enum):
    Skip = auto()
    Create = auto()
    CreateAndPush = auto()

    @property
    def should_create(self) -> bool:
        return self != GitAction.Skip


@dataclass
class GitActions:
    commit: GitAction = GitAction.Create
    branch: GitAction = GitAction.Skip
    tag: GitAction = GitAction.Skip

    def __post_init__(self) -> None:
        if self.commit == GitAction.Skip:
            if self.branch != GitAction.Skip:
                raise ValueError("if 'commit' is Skip, 'branch' must be DoNothing")
            if self.tag != GitAction.Skip:
                raise ValueError("if 'commit' is Skip, 'tag' must be DoNothing")

    @property
    def any_push(self) -> bool:
        return any(
            action == GitAction.CreateAndPush
            for action in (self.commit, self.branch, self.tag)
        )


@dataclass
class GitConfig:
    remote: str = DEFAULT_REMOTE
    commit_format_pattern: str = DEFAULT_COMMIT_PATTERN
    branch_format_pattern: str = DEFAULT_BRANCH_PATTERN
    tag_format_pattern: str = DEFAULT_TAG_PATTERN
    actions: GitActions = field(default_factory=GitActions)
