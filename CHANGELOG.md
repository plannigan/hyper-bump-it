# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Documentation link to package metadata.

### Fixed

* Reject file globs that attempt to access files outside of the project root.
* Warning before replacing an existing configuration with project initialization.
* Interactive project initialization more clearly describes explict replace format pattern.
* Interactive project initialization now shows recently provided search pattern when addressing
    issues with a file definition that omitted the replace format pattern.
* Update development status classifier.

## [0.5.0] - 2023-08-04

### Added

* Support for signing commits and tags.
* Support for including a message on a tag.

### Fixed

* Incorrectly adding untracked files when creating a commit.

### Changed

* **BREAKING**: `tag_format_pattern` renamed to `tag_name_format_pattern`.

## [0.4.1] - 2023-05-07

### Internal

* Update `typer` to use custom types and `Annotated` declaration style.
* Update to `pydantic` 2.0.
* Use OpenID Connect as a [trusted publisher][trusted-publishers] for uploading releases.

## [0.4.0] - 2023-02-27

### Added

* `--patch` as command line options to display the planned changes as a patch instead of performing
    any operations.
* Multi-line search and replacement patterns.
* Match arbitrary dates when `today` key is used in a search format pattern.

### Changed

* Display planned changes as a unified diff instead of a custom format.

### Fixed

* Configuration file line endings changed to system default when updating file.

## [0.3.1] - 2023-02-11

### Fixed

* Incorrectly display of planned change for lines that contained leading whitespace characters.
* Incorrectly display of text containing square brackets (`[`, `]`).
* Inconsistent display of file and directory paths (absolute vs relative path).
* Crash when format pattern contained an integer key name or no key name.
* Inconsistent colors of displayed text.
* Minor typos in displayed text.

## [0.3.0] - 2023-01-26

### Added

* Ability to limit allowed starting branch.
* Can be run as a module in addition to the entrypoint script.

### Fixed

* Value of `hyper_bump_it.__version__`.

### Internal

* Use `hyper-bump-it` to manage the version of the project.
* Automate the release process of new versions.
* Reorganize internal modules under a single internal sub-module.
* Remove dependency on `semantic-version`.

## [0.2.0] - 2023-01-11

### Added

* Controls related to the interactive confirmation prompt
    * `show_confirm_prompt` in configuration file can explicitly enable (default) or disable the
        prompt.
    * `-y` & `--yes` as command line options to disable the prompt.
    * `--interactive` as command line options to explicitly enable the prompt.
    * `-n` & `--no` command line options as aliases for `--dry-run`.
* Command line command to initialize a project.
* Name of remote repository to displayed description for push action.
* Support for `rich` v13.x.

### Fixed

* Crash when executing against a repository without any commits. A clear error message is displayed
    instead.
* Unclear text displayed for proposed execution plan description when compared to text displayed
    when executing the plan.

## [0.1.0] - 2022-12-16

First functional release

## [0.0.1] - 2022-10-26

Initial Release (not functional yet)

[trusted-publishers]: https://docs.pypi.org/trusted-publishers/
