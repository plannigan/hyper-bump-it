# Why hyper-bump-it?

There are multiple other version bumping tools available. Before creating `hyper-bump-it`, I had
used [bump2version][bump2version] and [tbump][tbump]. However, each time I would end up writing a
script to wrap the tool to get the full functionality I desired.

This page covers some of the more significant differences between `hyper-bump-it`, `bump2version`,
and `tbump`[^1]. This includes some things that are not supported by `hyper-bump-it`[^2].

## Key Differences

### Branch Version Control Support

Both `bump2version` and `tbump` support committing and tagging the change in the local repository.
However, it is common to not allow pushing directly to the default branch of a repository.

`hyper-bump-it` can be used to create a branch for the commit that updates the version. This branch
can then be push and merged as part of a pull request.

### Push Version Control Support

`bump2version` can only make changes to the local repository. `tbump` can push changes to the
remote repository (and will do that by default).

`hyper-bump-it` can push changes to the remote repository, but will only do that when configured to
do so.

### Current Version from File

Most software build/release tools already have an authoritative place for the version to be stored.
`hyper-bump-it` can be configured to extract the current version for that file (see
[Current Version][current-version]). This has the added benefit of the configuration file not being
edited every time version is updated.

This functionality is optional. Explicitly listing the current version in the configuration file
is supported in the same way as done in `bump2version` and `tbump`.

### TOML Configuration File

`bump2version` uses an [INI configuration file][ini]. However, that file format does not have a
standard specification and different implementation have varying support for some features.

`hyper-bump-it` and `tbump` use a [TOML][toml] configuration files. The specification of this
file format ensures that there are no ambiguities. It is straight forward for people to read and
programs to parse. The requirement for quoting strings resolves potential issues that can arise
when dealing with multi-line string and/or strings that contain comment characters.

### Multiline Search & Replacement Patterns

`hyper-bump-it` and `bump2version` support search or replacement patterns that span multiple lines.
This can be helpful for dealing with ambiguities in a file that needs to be updated or adding
multiple lines of text as part of the update.

`tbump` does not have support for this feature.

### Mercurial Support

`bump2version` can work with projects that use Mercurial or Git.

`hyper-bump-it` and `tbump` only support Git.

### Custom Version Schemes

`hyper-bump-it` assumes that the full version is compatible with the [semantic versioning][semver]
specification.

`bump2version` and `tbump` allow for fully customized version. However, this doesn't
mean that every file must contain the full version (see [Format Patterns][format-patterns]).

## Table of Differences

| Feature                                  | hyper-bump-it | bump2version | tbump         |
|------------------------------------------|---------------|--------------|---------------|
| [VCS Branching][branching]               | Yes           | No           | No            |
| [VCS Push][pushing]                      | Yes (opt-in)  | No           | Yes (opt-out) |
| [Current Version from File][keystone]    | Yes           | No           | No            |
| [Configuration File Format][config-file] | TOML          | INI          | TOML          |
| [Multiline Search & Replace][multiline]  | Yes           | Yes          | No            |
| Git                                      | Yes           | Yes          | Yes           |
| Mercurial                                | No            | Yes          | No            |
| [Custom Version Schemes][version-scheme] | No            | Yes          | Yes           |

[^1]:
    As of the writing of this page (2023-02-20).
[^2]:
    Support for these feature could be added in the future.

[bump2version]: https://github.com/c4urself/bump2version
[tbump]: https://github.com/your-tools/tbump
[current-version]: ./usage-guide/configuration.md#current-version
[ini]: https://en.wikipedia.org/wiki/INI_file
[toml]: https://toml.io/
[semver]: https://semver.org/
[format-patterns]: ./usage-guide/format-patterns.md

[branching]: #branch-version-control-support
[pushing]: #push-version-control-support
[keystone]: #current-version-from-file
[config-file]: #toml-configuration-file
[multiline]: #multiline-search--replacement-patterns
[version-scheme]: #custom-version-schemes
