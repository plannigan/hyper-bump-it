# Configuration

`hyper-bump-it` is configured using a file in the [TOML format][toml]. The default name for this
file is `hyper-bump-it.toml` and it is expected to be in the root directory of the project. The
command line interface (CLI) allows specifying an alternate path for this file.

!!! note "pyproject.toml Support"

    For Python projects, `pyproject.toml` is a standard file that can contain configuration
    information for multiple different tools. `hyper-bump-it` also supports reading the
    configuration from this file. This will only be checked for if `hyper-bump-it.toml` is not
    found and the CLI did not specify an alternate path.

## Configuration File

All configuration sections are rooted under the `hyper-bump-it` table. Most settings have
reasonable defaults, so the following is a functional configuration.

!!! note "pyproject.toml Support"

    When using `pyproject.toml`, configuration sections are rooted under the `tool.hyper-bump-it`
    table instead of simply `hyper-bump-it`.

=== "hyper-bump-it.toml"
    ```toml
    [hyper-bump-it]
    current_version = "1.2.3"

    [[hyper-bump-it.files]]
    file_glob = "*.txt"
    ```

=== "pyproject.toml"
    ```toml
    [tool.hyper-bump-it]
    current_version = "1.2.3"

    [[tool.hyper-bump-it.files]]
    file_glob = "*.txt"
    ```

### Top Level Table

There are a few fields that can be specified as part of the top level table.

The most common is the `current_version` field, which contains the current version. How this is
used and the alternative option are discussed in a [latter section][current-version-keystone].

The other optional field is `show_confirm_prompt`. If this field is not specified (default) or set
to `true`, `hyper-bump-it` will prompt the user to confirm the changes described in the execution
plan before performing the actions. When set to `false`, the prompt will **not** be displayed.
Instead, the actions will be immediately performed.

The following is an example configuration which disables the confirmation prompt.

=== "hyper-bump-it.toml"
    ```toml
    [hyper-bump-it]
    current_version = "1.2.3"
    show_confirm_prompt = false

    [[hyper-bump-it.files]]
    file_glob = "*.txt"
    ```

=== "pyproject.toml"
    ```toml
    [tool.hyper-bump-it]
    current_version = "1.2.3"
    show_confirm_prompt = false

    [[tool.hyper-bump-it.files]]
    file_glob = "*.txt"
    ```

### Files

The most important part of the configuration is the list of file definitions. This is how
`hyper-bump-it` knows which files should be updated and how that update process should operate.
There **must** be at least one file definition.

The only field that each file definition is required to have is that `file_glob` field. This tells
`hyper-bump-it` which files should be updated. This can be an explicit file name, but
[glob patterns][glob] are also supported. Using a glob pattern allows for a single file definition
to be used to specify how multiple files should be updated. These file paths should be relative to
the project root.

In addition, `search_format_pattern` and `replace_format_pattern` fields can be included in a file
definition. The `search_format_pattern` specifies the text to look for in each file matched by
`file_glob`. While the `replace_format_pattern` specifies the text to write back to the file
in place of the text that was searched for. There is a dedicated page that discusses
[format patterns][format-patterns] in more detail.

If `search_format_pattern` is not specified, the default value of `"{version}"` is used. If
`replace_format_pattern` is not specified, the value of `search_format_pattern` is used.

There is an additional optional field named `keystone`, this is discussed in a
[latter section][current-version-keystone].

The following is an example configuration which has two file definitions that both customize the
`search_format_pattern`.

=== "hyper-bump-it.toml"
    ```toml
    [hyper-bump-it]
    current_version = "1.2.3"

    [[hyper-bump-it.files]]
    file_glob = "*.txt"
    search_format_pattern = "version={version}"

    [[hyper-bump-it.files]]
    file_glob = "index.md"
    search_format_pattern = "My Project - {major}.{minor}"
    ```

=== "pyproject.toml"
    ```toml
    [tool.hyper-bump-it]
    current_version = "1.2.3"

    [[tool.hyper-bump-it.files]]
    file_glob = "*.txt"
    search_format_pattern = "version={version}"

    [[tool.hyper-bump-it.files]]
    file_glob = "index.md"
    search_format_pattern = "My Project - {major}.{minor}"
    ```

### Git

The [`git` integration][git-integration] is configured within the dedicated sub-tables, but they
are completely optional.

#### Actions

There are three types of `git` actions that can be performed: `commit`, `branch`, and `tag`.
Each of these fields can have one of three values: `"skip"`, `"create"`, or `"create-and-push"`.
There is a dedicated section that discusses these [git actions][git-actions] in more detail.

To ensure changes are not accidentally published, none of the fields default to
`"create-and-push"`. If `commit` is not specified, the default value of `"create"` is used. If
`brnach` is not specified, the default value of `"skip"` is used. If `tag` is not specified, the
default value of `"skip"` is used.

#### Allowed Initial Branches

Further safety concerns can be addressed by limiting which branches `hypber-bump-it` will
execute on. By default, only `main` and `master` are allowed. `allowed_initial_branches`can be
used to customize the set of allowed branches. Explicitly using an empty list will disable this
functionality. If you want to allow additional branches in addition to the defaults,
`extend_allowed_initial_branches` can be used without needing to explicitly re-list the defaults.

#### Customize Operations

There are a few fields that can be used to customize how these actions operate.

* `remote` specifies the name of remote repository to use as the destination for push operations.
    If not specified, the default value of `"origin"` is used.
* `commit_format_pattern` is a [format pattern][format-patterns] used to produce the message for
    the commit. If not specified, the default value of
    `"Bump version: {current_version} → {new_version}"` is used.
* `branch_format_pattern` is a [format pattern][format-patterns] used to produce the name of the
    branch. If not specified, the default value of, the default value of
    `"bump_version_to_{new_version}"` is used.
* `tag_format_pattern` is a [format pattern][format-patterns] used to produce the name of the tag.
    If not specified, the default value of, the default value of `"v{new_version}"` is used.
* `tag_message_format_pattern` is a [format pattern][format-patterns] used to produce the message of
    the tag. If not specified, the default value of, the default value of
    `"Bump version: {current_version} → {new_version}"` is used.


#### Example

The following is an example configuration which creates a commit on a new branch that is pushed to
the "upstream" remote. Additionally, the format patterns for the commit message and branch names
are customized.

=== "hyper-bump-it.toml"
    ```toml
    [hyper-bump-it]
    current_version = "1.2.3"

    [hyper-bump-it.git]
    remote = "upstream"
    commit_format_pattern = "Bump version to {new_version}"
    branch_format_pattern = "bump_to_{new_version}"

    [hyper-bump-it.git.actions]
    commit = "create-and-push"
    branch = "create-and-push"

    [[hyper-bump-it.files]]
    file_glob = "*.txt"
    ```

=== "pyproject.toml"
    ```toml
    [tool.hyper-bump-it]
    current_version = "1.2.3"

    [tool.hyper-bump-it.git]
    remote = "upstream"
    commit_format_pattern = "Bump version to {new_version}"
    branch_format_pattern = "bump_to_{new_version}"

    [tool.hyper-bump-it.git.actions]
    commit = "create-and-push"
    branch = "create-and-push"

    [[tool.hyper-bump-it.files]]
    file_glob = "*.txt"
    ```

### Current Version

By default, the current version is explicitly recorded in the configuration file using the
`current_version` field. As a result, this means that each time `hyper-bump-it` is used to change
the version number, that configuration file will also change.

For some, this behavior might not be desirable. Most projects already have a that acts as the
authoritative source for the software version when the release artifact is generated.
`hyper-bump-it` allows projects to indicate this file with the `keystone` setting as part of a file
table.

The following is an example configuration has a single file definitions, which is a keystone file.
Default values are used for all other fields.

=== "hyper-bump-it.toml"
    ```toml
    [[hyper-bump-it.files]]
    file_glob = "version.txt"
    keystone = true
    ```

=== "pyproject.toml"
    ```toml
    [[tool.hyper-bump-it.files]]
    file_glob = "version.txt"
    keystone = true
    ```

!!! note

    Since `current_version` is not used when using a keystone file, the top level table can be 
    omitted.

The `search_format_pattern` will be used to parse the specified file to discover the current
version.

With this functionality enabled, there are a few restrictions:

* The configuration file **must not** specify the `current_version` field.
* Specifying a glob pattern instead of an explicit file name for `file_glob` is still supported.
    However, it **must** only match a single file.
* The `search_format_pattern` can contain any of the [supported keys][supported-keys]. However,
    it is important to [understand how the pattern is processed][keystone-considerations].


[toml]: https://toml.io/
[glob]: https://docs.python.org/3/library/glob.html
[format-patterns]: format-patterns.md
[current-version-keystone]: #current-version
[git-integration]: git-integration.md
[git-actions]: git-integration.md#actions
[supported-keys]: format-patterns.md#supported-keys
[keystone-considerations]: format-patterns.md#keystone-file-considerations