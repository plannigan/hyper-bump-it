from itertools import product
from typing import TypedDict

from hyper_bump_it._hyper_bump_it.config import GitAction


class GitActionCombination(TypedDict):
    commit: GitAction
    branch: GitAction
    tag: GitAction


INVALID_COMBINATIONS: list[tuple[GitActionCombination, str]] = []
for key, action in product(
    ["branch", "tag"], [GitAction.Create, GitAction.CreateAndPush]
):
    # default everything to skip, but then overwrite given key
    combination = {
        "commit": GitAction.Skip,
        "branch": GitAction.Skip,
        "tag": GitAction.Skip,
        key: action,
    }
    INVALID_COMBINATIONS.append(
        (
            combination,
            f"if commit is 'skip', {key} must also be 'skip'",
        )
    )
for tag in [GitAction.Skip, GitAction.Create]:
    INVALID_COMBINATIONS.append(
        (
            {"commit": GitAction.Create, "branch": GitAction.CreateAndPush, "tag": tag},
            "if branch is 'create-and-push', 'commit' must also be 'create-and-push'",
        )
    )
for branch in [GitAction.Skip, GitAction.Create]:
    INVALID_COMBINATIONS.append(
        (
            {
                "commit": GitAction.Create,
                "branch": branch,
                "tag": GitAction.CreateAndPush,
            },
            "if tag is 'create-and-push', 'commit' must also be 'create-and-push'",
        )
    )
for tag in iter(GitAction):
    INVALID_COMBINATIONS.append(
        (
            {
                "commit": GitAction.CreateAndPush,
                "branch": GitAction.Create,
                "tag": tag,
            },
            "if branch is 'create', commit must also be 'create'",
        )
    )
