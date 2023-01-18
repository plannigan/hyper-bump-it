[![CI pipeline status](https://github.com/plannigan/hyper-bump-it/actions/workflows/main.yml/badge.svg?branch=main)][ci]
[![PyPI](https://img.shields.io/pypi/v/hyper-bump-it)][pypi]
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hyper-bump-it)][pypi]
[![codecov](https://codecov.io/gh/plannigan/hyper-bump-it/branch/main/graph/badge.svg?token=V4DADJU0BI)][codecov]
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)][mypy-home]
[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)][black-home]

# Hyper Bump It

A version bumping tool.

`hyper-bump-it`'s features include:
* Updating the version to a new fully specified value
* Increasing the version base on a specific version part
* Optional Git integrations:
    * Commit changes
    * Create a new branch or tag
    * Push changes to a remote repository
* Customizable search and replacement patterns
* Safe by default, but can be overridden:
    * Request confirmation before editing files
    * Explicit configuration need to push changes
    * Won't run if the current branch is not the default
    * Won't run if there are unstaged changes
* TOML configuration file (can be part of `pyproject.toml`)

## Examples

This first example

* Updates to an explicit new version
* Updates multiple files that had lines matching the search pattern
* Commits those changes to a newly created branch

```commandline
$ hyper-bump-it to 2.3.4
Create branch bump_version_to_2.3.4
Switch to branch bump_version_to_2.3.4
Updating version in configuration file
Update files
────────────────────────────── example/foo.txt ──────────────────────────────
2: - --1.2.3--abc
2: + --2.3.4--abc
6: - --1.2.3--edf
6: + --2.3.4--edf
────────────────────────────── example/bar.txt ──────────────────────────────
2: - more --1.2.3-- text
2: + more --2.3.4-- text
Commit changes: Bump version: 1.2.3 → 2.3.4
Switch to branch main
Do you want to perform these actions? [y/n] (n): y
Creating branch bump_version_to_2.3.4
Switching to branch bump_version_to_2.3.4
Updating version in configuration file
Update files
Updating example/foo.txt
Updating example/bar.txt
Committing changes: Bump version: 1.2.3 → 2.3.4
Switching to branch main
```

This second example

* Updates to the next minor version
* Updates multiple files that had lines matching the search pattern
* Commits those changes, tags the new commit, and pushes the changes to the remote repository

```commandline
$ hyper-bump-it by minor
Updating version in configuration file
Update files
────────────────────────────── example/foo.txt ──────────────────────────────
2: - --1.2.3--abc
2: + --1.3.0--abc
6: - --1.2.3--edf
6: + --1.3.0--edf
────────────────────────────── example/bar.txt ──────────────────────────────
2: - more --1.2.3-- text
2: + more --1.3.0-- text
Commit changes: Bump version: 1.2.3 → 1.3.0
Tag commit: v1.3.0
Pushing commit with tag v1.3.0
Do you want to perform these actions? [y/n] (n): y
Updating version in configuration file
Update files
Updating example/foo.txt
Updating example/bar.txt
Committing changes: Bump version: 1.2.3 → 1.3.0
Tagging commit: v1.3.0
Pushing commit with tag v1.3.0
```

[ci]: https://github.com/plannigan/hyper-bump-it/actions
[pypi]: https://pypi.org/project/hyper-bump-it/
[codecov]: https://codecov.io/gh/plannigan/hyper-bump-it
[mypy-home]: http://mypy-lang.org/
[black-home]: https://github.com/psf/black
