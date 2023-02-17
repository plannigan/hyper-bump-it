# Getting Started

## Installation

To install `hyper-bump-it`, simply run this simple command in your terminal of choice:

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

### Automated Initialization

To help users start using `hyper-bump-it` for the first time, the `init` command is provided to
help initialize the configuration file. The default mode of operation for this command is to show a
series of interactive prompts that will allow for fully customizing the configuration. The
following shows an example that changes format pattern used to create the commit message.

=== "hyper-bump-it.toml"
    ```commandline
    $ hyper-bump-it init 1.2.3
    What part of configuration would you like to edit?
    general - Top level settings that don't fit in a specific category
    files - File matching settings
    git - Git integration settings
    done - Stop editing and write out the configuration (default)
    Enter the option name: git
    What part of configuration would you like to edit?
    remote - Name of remote to use when pushing changes
    commit - Format pattern to use for commit message
    branch - Format pattern to use for branch name
    tag - Format pattern to use for tag name
    actions - Configure what Git actions should be performed
    done - Stop editing the Git integration settings (default)
    Enter the option name: commit
    Format patterns are used to generate text. The format pattern for commit message is currently set to: Bump version: {current_version} → {new_version} (the default)
    Enter a new format pattern or leave it blank to keep the value: Bump to version: {current_version}
    What part of configuration would you like to edit?
    remote - Name of remote to use when pushing changes
    commit - Format pattern to use for commit message
    branch - Format pattern to use for branch name
    tag - Format pattern to use for tag name
    actions - Configure what Git actions should be performed
    done - Stop editing the Git integration settings (default)
    Enter the option name: done
    What part of configuration would you like to edit?
    general - Top level settings that don't fit in a specific category
    files - File matching settings
    git - Git integration settings
    done - Stop editing and write out the configuration (default)
    Enter the option name: done

    $ cat hyper-bump-it.toml 
    [hyper-bump-it]
    current_version = "1.2.3"
    [[hyper-bump-it.files]]
    file_glob = "version.txt"

    [hyper-bump-it.git]
    commit_format_pattern = "Bump to version: {current_version}"
    ```

=== "pyproject.toml"
    ```commandline
    $ hyper-bump-it init --pyproject 1.2.3
    What part of configuration would you like to edit?
    general - Top level settings that don't fit in a specific category
    files - File matching settings
    git - Git integration settings
    done - Stop editing and write out the configuration (default)
    Enter the option name: git
    What part of configuration would you like to edit?
    remote - Name of remote to use when pushing changes
    commit - Format pattern to use for commit message
    branch - Format pattern to use for branch name
    tag - Format pattern to use for tag name
    actions - Configure what Git actions should be performed
    done - Stop editing the Git integration settings (default)
    Enter the option name: commit
    Format patterns are used to generate text. The format pattern for commit message is currently set to: Bump version: {current_version} → {new_version} (the default)
    Enter a new format pattern or leave it blank to keep the value: Bump to version: {current_version}
    What part of configuration would you like to edit?
    remote - Name of remote to use when pushing changes
    commit - Format pattern to use for commit message
    branch - Format pattern to use for branch name
    tag - Format pattern to use for tag name
    actions - Configure what Git actions should be performed
    done - Stop editing the Git integration settings (default)
    Enter the option name: done
    What part of configuration would you like to edit?
    general - Top level settings that don't fit in a specific category
    files - File matching settings
    git - Git integration settings
    done - Stop editing and write out the configuration (default)
    Enter the option name: done

    $ cat pyproject.toml
    [tool.other]
    foo = "hello world"
    [tool.hyper-bump-it]
    current_version = "1.2.3"
    [[tool.hyper-bump-it.files]]
    file_glob = "version.txt"

    [tool.hyper-bump-it.git]
    commit_format_pattern = "Bump to version: {current_version}"
    ```

There is an alternate mode accessed by providing the `--non-interactive` option. This will write
out the configuration based only on values specified with command line options. The following shows
the most basic form of this mode.

=== "hyper-bump-it.toml"
    ```commandline
    $ hyper-bump-it init --non-interactive 1.2.3
    Non-interactive mode: A sample configuration will be written that will need manual edits.
    $ cat hyper-bump-it.toml
    [hyper-bump-it]
    current_version = "1.2.3"
    [[hyper-bump-it.files]]
    file_glob = "version.txt"
    ```

=== "pyproject.toml"
    ```commandline
    $ hyper-bump-it init --non-interactive --pyproject 1.2.3
    Non-interactive mode: A sample configuration will be written that will need manual edits.
    $ cat pyproject.toml
    [tool.other]
    foo = "hello world"
    [tool.hyper-bump-it]
    current_version = "1.2.3"
    [[tool.hyper-bump-it.files]]
    file_glob = "version.txt"
    ```

There are many more options that can be used to further customize the configuration, when using
this mode. `hyper-bump-it init --help` will show the options not covered here.

!!! tip
    See the [configuration page][configuration] for how to utilize `pyproject.toml` instead of a
    dedicated configuration file.

## Example Executions

Using the configuration shown above, lets see how `hyper-bump-it` runs.

```commandline
$ hyper-bump-it to 2.3.4
Execution Plan:
Update version in configuration file
Update files
────────────────────────────── version.txt ──────────────────────────────
--- version.txt
+++ version.txt
@@ -1,3 +1,3 @@
 hello
-version="1.2.3"
+version="2.3.4"
 world

Commit changes: Bump version: 1.2.3 → 2.3.4

Do you want to perform these actions? [y/n] (n): y
Updating version in configuration file
Updating files
Updating version.txt
Committing changes: Bump version: 1.2.3 → 2.3.4
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
$ hyper-bump-it by minor
Updating version in configuration file
Update files
────────────────────────────── version.txt ──────────────────────────────
--- version.txt
+++ version.txt
@@ -1,3 +1,3 @@
 hello
-version="1.2.3"
+version="1.3.0"
 world

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
