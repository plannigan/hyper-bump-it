# Git Integration

In addition to updating a specified set of files, `hyper-bump-it` can interact with the projects
version control system. This functionality will automate some of the action that would need to be
performed manually after updating files.

## Requirements

`hyper-bump-it` depends on the `git` executable to be installed and available on the system path.
([GitPython][git-python] is used under the covers to interact with `git`).

The local checkout of the project is expected to have the `.git/` directory at the same level as
the project root.

!!! tip

    These requirements are only enforced when `hyper-bump-it` is configured to perform `git`
    actions. When all of the actions are set to `"skip"`, the `git` funcitonality will not be
    initialized.

## Actions

There are three types of `git` actions that can be performed: commit, branch, and tag.

* The commit action is the most basic. It is the process of creating a new commit that contains the
    files that were updated by `hyper-bump-it`.
* The branch action can be used to augment the commit action. When used, a new branch is created 
    and the new commit is added to that new branch instead of the branch that was active when
    `hyper-bump-it` started executing.
* The tag action can be used to as a step following the commit action. When used, it creates a new
    tag that points to the new commit.

## Valid action states

Each of the git operations can be configured to be `"skip"`, `"create"`, or `"create-ane-push"`.
However, many of the combinations that are possible are not allowed because they would require a
result that is not possible.

There are a few basic rules:

* If the files are being edited without creating a commit (commit action is set to `"skip"`), branch
    and tag **must** also be set to `"skip"`.
* If a commit is being created, but not pushed (commit action is set to `"create"`), branch and tag
    **must not** be set to `"create-and-push"`.
* If a commit is being created & pushed (commit action is set to `"create-and-push"`), branch
    **must not** be  set to `"create"`.

[git-python]: https://gitpython.readthedocs.io/
