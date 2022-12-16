# Getting Started

## Installation

To install `columbo`, simply run this simple command in your terminal of choice:

```bash
python -m pip install hyper-bump-it
```

## Initial Setup

Before `hyper-bump-it` can do any work, it needs to be configured. This configuration allows it to
know which files should be operated on and how. A simple config file named `hyper-bump-it.toml` can
be seen below:

```toml linenums="1"
[hyper-bump-it]
current_version = "1.2.3"

[[hyper-bump-it.files]]
file_glob = "version.txt"
search_format_pattern = "version=\"{version}\""
```

* Line 2: Specifies the current version of the project being configured. Edit this value to match
    the version for the latest release of the project.
* Line 4-6: Define a single file definition.
* Line 5: Specifies the name of a file to be updated.
* Line 6: Specifies the text to look for in that file and replace with the new version.

!!! info 
    A future release will provide an `init` command that can be used to create and initial
    configuration.

!!! tip
    See the [configuration page][configuration] for how to utilize `pyproject.toml` instead of a
    dedicated configuration file.

## Example Executions

Using the configuration shown above, lets see how `hyper-bump-it` runs.

```commandline
hyper-bump-it to 2.3.4
Updating version in configuration file
Update files
────────────────────────────── version.txt ──────────────────────────────
2: - version="1.3.0"
2: + version="2.3.4"
Commit changes: Bump version: 1.3.0 → 2.3.4
Do you want to perform these actions? [y/n] (n): y
Updating version in configuration file
Update files
Updating version.txt
Committing changes: Bump version: 1.3.0 → 2.3.4
```

`hyper-bump-it` finds the file with the version text and displays the changes it plans to make.
After the user confirms the change, the program continues with editing the files.

Included in the execution plan is committing the changes to the local `git` checkout. The example
configuration file did not specify any specific options, so `hyper-bump-it` defaulted to simply
committing the changes.

In addition to updating the version to a specific value, `hyper-bump-it` can also do version
increments. The following example show `hyper-bump-it` updating the version, from the original
state, to the next minor version.

```commandline
hyper-bump-it by minor
Updating version in configuration file
Update files
────────────────────────────── version.txt ──────────────────────────────
2: - version="1.3.0"
2: + version="1.4.0"
Commit changes: Bump version: 1.3.0 → 1.4.0
Do you want to perform these actions? [y/n] (n): y
Updating version in configuration file
Update files
Updating version.txt
Committing changes: Bump version: 1.3.0 → .1.4.0
```

## What's Next?

Read about all the [configuration options][configuration] for a more detailed description of how to
get `hyper-bump-it` to work best for a specific project.

Read about how `hyper-bump-it` can [integrate with `git`][git-integration] to learn more about how
to automate things like creating a branch, pushing a change, and creating a tag.

Read about how [format patterns][format-patterns] can be used to customize how text is matched and
updated.

[configuration]: usage-guide/configuration.md
[git-integration]: usage-guide/git-integration.md
[format-patterns]: usage-guide/format-patterns.md
