from pathlib import Path

import pytest

from hyper_bump_it._hyper_bump_it.config import keystone_parser
from hyper_bump_it._hyper_bump_it.error import (
    IncompleteKeystoneVersionError,
    VersionNotFound,
)
from hyper_bump_it._hyper_bump_it.format_pattern import keys
from hyper_bump_it._hyper_bump_it.version import Version

SOME_FILE = "foo.txt"


@pytest.mark.parametrize(
    ["description", "pattern", "expected_version", "file_content"],
    [
        (
            "explicit version",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}",
            Version.parse("1.2.3"),
            "1.2.3",
        ),
        (
            "explicit version, odd ordering",
            f"{{{keys.PATCH}}} - {{{keys.MINOR}}} {{{keys.MAJOR}}}",
            Version.parse("1.2.3"),
            "3 - 2 1",
        ),
        (
            "with prerelease",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}-{{{keys.PRERELEASE}}}",
            Version.parse("1.2.3-a"),
            "1.2.3-a",
        ),
        (
            "with build",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}+{{{keys.BUILD}}}",
            Version.parse("1.2.3+a"),
            "1.2.3+a",
        ),
        (
            "with prerelease and build",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}-{{{keys.PRERELEASE}}}+{{{keys.BUILD}}}",
            Version.parse("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "current keys with prerelease and build",
            f"{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}.{{{keys.CURRENT_PATCH}}}-{{{keys.CURRENT_PRERELEASE}}}+{{{keys.CURRENT_BUILD}}}",
            Version.parse("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "fast path version",
            f"{{{keys.VERSION}}}",
            Version.parse("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "fast path current version",
            f"{{{keys.CURRENT_VERSION}}}",
            Version.parse("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "not first line of file",
            f"{{{keys.VERSION}}}",
            Version.parse("1.2.3-p+a"),
            "foo bar\n1.2.3-p+a\nbazz",
        ),
        (
            "current general takes precedence",
            f"{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}.{{{keys.CURRENT_PATCH}}}-{{{keys.CURRENT_PRERELEASE}}}+{{{keys.CURRENT_BUILD}}}"
            f" {{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}-{{{keys.PRERELEASE}}}+{{{keys.BUILD}}}",
            Version.parse("1.2.3-p+a"),
            "11.22.33-pp+aa 1.2.3-p+a",
        ),
        (
            "fast path current general takes precedence",
            f"{{{keys.CURRENT_VERSION}}} {{{keys.VERSION}}}",
            Version.parse("1.2.3-p+a"),
            "11.22.33-pp+aa 1.2.3-p+a",
        ),
        (
            "multiline pattern - extra specific",
            f"edf\n{{{keys.VERSION}}}",
            Version.parse("1.2.3-p+a"),
            "abc\n11.22.33-pp+aa\nedf\n1.2.3-p+a\n",
        ),
        (
            "multiline pattern - values split",
            f"{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}\n{{{keys.CURRENT_PATCH}}}",
            Version.parse("1.2.3"),
            "1.2\n3",
        ),
    ],
)
def test_find_current_version__valid_pattern_match__found(
    pattern, expected_version, file_content, description, tmp_path: Path
):
    file = tmp_path / SOME_FILE
    file.write_text(file_content)

    assert (
        keystone_parser.find_current_version(file, pattern) == expected_version
    ), description


@pytest.mark.parametrize(
    ["pattern", "file_content"],
    [
        (f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}", "1.2"),
        (f"{{{keys.MAJOR}}}.{{{keys.PATCH}}}", "1.2"),
        (f"{{{keys.MINOR}}}.{{{keys.PATCH}}}", "1.2"),
    ],
)
def test_find_current_version__missing_required_part__error(
    pattern, file_content, tmp_path: Path
):
    file = tmp_path / SOME_FILE
    file.write_text(file_content)

    with pytest.raises(IncompleteKeystoneVersionError):
        keystone_parser.find_current_version(file, pattern)


@pytest.mark.parametrize(
    ["pattern", "file_content"],
    [
        (f"{{{keys.NEW_MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}", "1.2.3"),
        (f"{{{keys.MAJOR}}}.{{{keys.NEW_MINOR}}}.{{{keys.PATCH}}}", "1.2.3"),
        (f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.NEW_PATCH}}}", "1.2.3"),
    ],
)
def test_find_current_version__new_part__ignored_causing_error(
    pattern, file_content, tmp_path: Path
):
    file = tmp_path / SOME_FILE
    file.write_text(file_content)

    with pytest.raises(IncompleteKeystoneVersionError):
        keystone_parser.find_current_version(file, pattern)


def test_find_current_version__not_found__error(tmp_path: Path):
    file = tmp_path / SOME_FILE
    file.touch()

    with pytest.raises(VersionNotFound):
        keystone_parser.find_current_version(file, "foo")
