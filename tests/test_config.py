import pytest

from hyper_bump_it._config import GitAction, GitActions


@pytest.mark.parametrize(
    "branch_action",
    [
        GitAction.Create,
        GitAction.CreateAndPush,
    ],
)
def test_git_actions__commit_nothing_branch_something__error(branch_action: GitAction):
    with pytest.raises(ValueError, match="branch"):
        GitActions(
            commit=GitAction.DoNothing, branch=branch_action, tag=GitAction.DoNothing
        )


@pytest.mark.parametrize(
    "tag_action",
    [
        GitAction.Create,
        GitAction.CreateAndPush,
    ],
)
def test_git_actions__commit_nothing_tag_something__error(tag_action: GitAction):
    with pytest.raises(ValueError, match="tag"):
        GitActions(
            commit=GitAction.DoNothing, tag=tag_action, branch=GitAction.DoNothing
        )
