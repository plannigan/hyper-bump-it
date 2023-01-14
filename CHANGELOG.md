# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Internal

* Reorganize internal modules under a single internal sub-module.

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
