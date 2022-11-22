from enum import Enum

from hyper_bump_it._text_formatter import keys


class GitAction(str, Enum):
    Skip = "skip"
    Create = "create"
    CreateAndPush = "create-and-push"

    @property
    def should_create(self) -> bool:
        return self != GitAction.Skip


DEFAULT_COMMIT_ACTION = GitAction.Create
DEFAULT_BRANCH_ACTION = GitAction.Skip
DEFAULT_TAG_ACTION = GitAction.Skip

DEFAULT_REMOTE = "origin"
DEFAULT_COMMIT_FORMAT_PATTERN: str = (
    f"Bump version: {{{keys.CURRENT_VERSION}}} → {{{keys.NEW_VERSION}}}"
)
DEFAULT_BRANCH_FORMAT_PATTERN = f"bump_version_to_{{{keys.NEW_VERSION}}}"
DEFAULT_TAG_FORMAT_PATTERN = f"v{{{keys.NEW_VERSION}}}"
DEFAULT_SEARCH_PATTERN = f"{{{keys.VERSION}}}"

HYPER_CONFIG_FILE_NAME = "hyper-bump-it.toml"
PYPROJECT_FILE_NAME = "pyproject.toml"


def validate_git_action_combination(
    commit: GitAction, branch: GitAction, tag: GitAction
) -> None:
    if not commit.should_create:
        if branch.should_create:
            raise ValueError("if commit is 'skip', branch must also be 'skip'")
        if tag.should_create:
            raise ValueError("if commit is 'skip', tag must also be 'skip'")
    if commit == GitAction.Create:
        if branch == GitAction.CreateAndPush:
            raise ValueError(
                "if branch is 'create-and-push', 'commit' must also be 'create-and-push'"
            )
        if tag == GitAction.CreateAndPush:
            raise ValueError(
                "if tag is 'create-and-push', 'commit' must also be 'create-and-push'"
            )
    if commit == GitAction.CreateAndPush and branch == GitAction.Create:
        raise ValueError("if branch is 'create', commit must also be 'create'")
