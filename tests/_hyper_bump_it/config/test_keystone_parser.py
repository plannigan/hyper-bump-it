from pathlib import Path

import pytest
from semantic_version import Version

from hyper_bump_it._hyper_bump_it.config import keystone_parser
from hyper_bump_it._hyper_bump_it.error import (
    FormatKeyError,
    FormatPatternError,
    IncompleteKeystoneVersionError,
    TodayFormatKeyError,
    VersionNotFound,
)
from hyper_bump_it._hyper_bump_it.text_formatter import keys
from tests._hyper_bump_it import sample_data as sd

SOME_FILE = "foo.txt"


@pytest.mark.parametrize(
    ["description", "format_pattern", "text_to_match"],
    [
        ("basic version", "{version}", "12.34.56"),
        ("basic version, part of a line", "{version}", "abc-12.34.56"),
        ("full version, pre-release & build", "{version}", "12.34.56-56ab+89xy"),
        ("full version, pre-release", "{version}", "12.34.56-56ab"),
        ("full version, build", "{version}", "12.34.56+89xy"),
        ("pieces", "{major}.{minor}.{patch}", "12.34.56"),
        ("pieces, different delimiters", "{major}*{minor}-{patch}", "12*34-56"),
    ],
)
def test_create_matching_pattern__some_format_pattern__can_match(
    format_pattern, text_to_match, description
):
    regex = keystone_parser._create_matching_pattern(format_pattern)

    assert regex.search(text_to_match) is not None, description


@pytest.mark.parametrize(
    ["description", "format_pattern", "text_to_match"],
    [
        ("partial version", "{version}", "12.34"),
        ("version, but different delimiters", "{version}", "12-34+56"),
    ],
)
def test_create_matching_pattern__some_format_pattern__not_match(
    format_pattern, text_to_match, description
):
    regex = keystone_parser._create_matching_pattern(format_pattern)

    assert regex.search(text_to_match) is None, description


@pytest.mark.parametrize(
    ["key", "expected_to_be_matched"],
    [
        (keys.CURRENT_VERSION, str(sd.SOME_VERSION)),
        (keys.CURRENT_MAJOR, str(sd.SOME_MAJOR)),
        (keys.CURRENT_MINOR, str(sd.SOME_MINOR)),
        (keys.CURRENT_PATCH, str(sd.SOME_PATCH)),
        (keys.CURRENT_PRERELEASE, sd.SOME_PRERELEASE),
        (keys.CURRENT_BUILD, sd.SOME_BUILD),
        (keys.NEW_VERSION, str(sd.SOME_OTHER_VERSION)),
        (keys.NEW_MAJOR, str(sd.SOME_OTHER_MAJOR)),
        (keys.NEW_MINOR, str(sd.SOME_OTHER_MINOR)),
        (keys.NEW_PATCH, str(sd.SOME_OTHER_PATCH)),
        (keys.NEW_PRERELEASE, sd.SOME_OTHER_PRERELEASE),
        (keys.NEW_BUILD, sd.SOME_OTHER_BUILD),
        (keys.VERSION, str(sd.SOME_VERSION)),
        (keys.MAJOR, str(sd.SOME_MAJOR)),
        (keys.MINOR, str(sd.SOME_MINOR)),
        (keys.PATCH, str(sd.SOME_PATCH)),
        (keys.PRERELEASE, sd.SOME_PRERELEASE),
        (keys.BUILD, sd.SOME_BUILD),
        (keys.TODAY, "1234-06-22"),
    ],
)
def test_create_matching_pattern__some_pattern__produces_regex_that_matches_group(
    key: str, expected_to_be_matched: str
):
    regex_pattern = keystone_parser._create_matching_pattern(f"{{{key}}}")

    match = regex_pattern.search(expected_to_be_matched)
    assert match is not None
    assert match.group(key) == expected_to_be_matched


TODAY_FORMAT_DIRECTIVE_MATCH_ARGS: list[tuple[str, str, str]] = [
    ("explicit default date format", "%Y-%m-%d", "1234-06-22"),
    ("smallest day of week", "%w", "0"),
    ("largest day of week", "%w", "6"),
    ("sub-10 day of month", "%d", "01"),
    ("10s day of month", "%d", "11"),
    ("20s day of month", "%d", "21"),
    ("30s day of month", "%d", "31"),
    ("smallest month of year", "%m", "01"),
    ("largest month of year", "%m", "12"),
    ("short year", "%y", "99"),
    ("sub-100 day of year", "%j", "001"),
    ("100s day of year", "%j", "156"),
    ("200s day of year", "%j", "289"),
    ("300s day of year", "%j", "366"),
    ("smallest day of week, 1 index", "%u", "1"),
    ("largest day of week, 1 index", "%u", "7"),
]


def _year(directive) -> list[tuple[str, str, str]]:
    return [
        ("smallest long year", directive, "0001"),
        ("largest long year", directive, "9999"),
    ]


def _week_of_year(directive) -> list[tuple[str, str, str]]:
    return [
        ("sub-10 week of year", directive, "01"),
        ("10s week of year", directive, "11"),
        ("20s week of year", directive, "21"),
        ("30s week of year", directive, "31"),
        ("40s week of year", directive, "41"),
        ("50s week of year", directive, "53"),
    ]


TODAY_FORMAT_DIRECTIVE_MATCH_ARGS.extend(_year("%Y"))
TODAY_FORMAT_DIRECTIVE_MATCH_ARGS.extend(_year("%G"))
TODAY_FORMAT_DIRECTIVE_MATCH_ARGS.extend(_week_of_year("%U"))
TODAY_FORMAT_DIRECTIVE_MATCH_ARGS.extend(_week_of_year("%W"))
TODAY_FORMAT_DIRECTIVE_MATCH_ARGS.extend(_week_of_year("%V"))


@pytest.mark.parametrize(
    ["description", "format_directives", "expected_to_be_matched"],
    TODAY_FORMAT_DIRECTIVE_MATCH_ARGS,
)
def test_create_matching_pattern__today_format_directive__produces_regex_that_matches_group(
    format_directives: str, expected_to_be_matched: str, description
):
    format_pattern = f"{{{keys.TODAY}:{format_directives}}}"
    regex_pattern = keystone_parser._create_matching_pattern(format_pattern)

    match = regex_pattern.search(expected_to_be_matched)
    assert match is not None, description
    assert match.group(keys.TODAY) == expected_to_be_matched, description


TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS: list[tuple[str, str, str]] = [
    ("explicit default date format, different ordering", "%Y-%m-%d", "06-22-1234"),
    ("explicit default date format, month to large", "%Y-%m-%d", "1234-13-06"),
    ("explicit default date format, day to large", "%Y-%m-%d", "1234-06-32"),
    ("smallest day of week, too long", "%w", "01"),
    ("largest day of week, too large", "%w", "7"),
    ("day of month, no leading 0", "%d", "1"),
    ("day of month, to large", "%d", "32"),
    ("day of month, to long", "%d", "321"),
    ("month of year, no leading 0", "%m", "1"),
    ("month of year, to large", "%m", "13"),
    ("month of year, much to large", "%m", "99"),
    ("short year, to small", "%y", "9"),
    ("short year, to large", "%y", "999"),
    ("day of year, too small", "%j", "67"),
    ("day of year, too large by a lot", "%j", "679"),
    ("day of week, 1 index, too small", "%u", "0"),
    ("day of week, 1 index, too large", "%u", "8"),
]


def _not_year(directive) -> list[tuple[str, str, str]]:
    return [
        ("long year, 1 digit", directive, "1"),
        ("long year, 2 digits", directive, "11"),
        ("long year, 3 digits", directive, "111"),
        ("long year, 5 digits", directive, "11111"),
        ("long year, not digit", directive, "a"),
    ]


def _not_week_of_year(directive) -> list[tuple[str, str, str]]:
    return [
        ("week of year, too short", directive, "1"),
        ("week of year, too long", directive, "990"),
        ("week of year, one too large", directive, "54"),
        ("week of year, too large a lot", directive, "99"),
        ("week of year, not digit", directive, "a"),
    ]


TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS.extend(_not_year("%Y"))
TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS.extend(_not_year("%G"))
TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS.extend(_not_week_of_year("%U"))
TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS.extend(_not_week_of_year("%W"))
TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS.extend(_not_week_of_year("%V"))


@pytest.mark.parametrize(
    ["description", "format_directives", "expected_not_to_match"],
    TODAY_FORMAT_DIRECTIVE_NOT_MATCH_ARGS,
)
def test_create_matching_pattern__today_format_directive_different__not_matches(
    format_directives: str, expected_not_to_match: str, description
):
    format_pattern = f"{{{keys.TODAY}:{format_directives}}}"
    regex_pattern = keystone_parser._create_matching_pattern(format_pattern)
    print(regex_pattern)

    match = regex_pattern.fullmatch(expected_not_to_match)
    assert match is None, description


@pytest.mark.parametrize(
    ["description", "invalid"],
    [
        ("invalid directive", "%1"),
        ("unsupported directive", "%a"),
    ],
)
def test_create_matching_pattern__today_format_directive_invalid__not_matches(
    invalid, description
):
    with pytest.raises(TodayFormatKeyError):
        keystone_parser._create_matching_pattern(f"{{{keys.TODAY}:{invalid}}}")


@pytest.mark.parametrize("key", sd.ALL_KEYS)
def test_create_matching_pattern__each_key__group_name_defined(key: str):
    # ensure that each key is usable & we didn't forget to add an explicit test case
    result = keystone_parser._create_matching_pattern(f"--{{{key}}}--")
    assert key in result.groupindex


def test_format__invalid_pattern__error():
    with pytest.raises(FormatPatternError):
        keystone_parser._create_matching_pattern("--{--")


def test_format__invalid_key__error():
    with pytest.raises(FormatKeyError):
        keystone_parser._create_matching_pattern("--{SOME_NOT_VALID_KEY}--")


@pytest.mark.parametrize(
    ["description", "pattern", "expected_version", "file_content"],
    [
        (
            "explicit version",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}",
            Version("1.2.3"),
            "1.2.3",
        ),
        (
            "explicit version, odd ordering",
            f"{{{keys.PATCH}}} - {{{keys.MINOR}}} {{{keys.MAJOR}}}",
            Version("1.2.3"),
            "3 - 2 1",
        ),
        (
            "with prerelease",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}-{{{keys.PRERELEASE}}}",
            Version("1.2.3-a"),
            "1.2.3-a",
        ),
        (
            "with build",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}+{{{keys.BUILD}}}",
            Version("1.2.3+a"),
            "1.2.3+a",
        ),
        (
            "with prerelease and build",
            f"{{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}-{{{keys.PRERELEASE}}}+{{{keys.BUILD}}}",
            Version("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "current keys with prerelease and build",
            f"{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}.{{{keys.CURRENT_PATCH}}}-{{{keys.CURRENT_PRERELEASE}}}+{{{keys.CURRENT_BUILD}}}",
            Version("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "fast path version",
            f"{{{keys.VERSION}}}",
            Version("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "fast path current version",
            f"{{{keys.CURRENT_VERSION}}}",
            Version("1.2.3-p+a"),
            "1.2.3-p+a",
        ),
        (
            "not first line of file",
            f"{{{keys.VERSION}}}",
            Version("1.2.3-p+a"),
            "foo bar\n1.2.3-p+a\nbazz",
        ),
        (
            "current general takes precedence",
            f"{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}.{{{keys.CURRENT_PATCH}}}-{{{keys.CURRENT_PRERELEASE}}}+{{{keys.CURRENT_BUILD}}}"
            f" {{{keys.MAJOR}}}.{{{keys.MINOR}}}.{{{keys.PATCH}}}-{{{keys.PRERELEASE}}}+{{{keys.BUILD}}}",
            Version("1.2.3-p+a"),
            "11.22.33-pp+aa 1.2.3-p+a",
        ),
        (
            "fast path current general takes precedence",
            f"{{{keys.CURRENT_VERSION}}} {{{keys.VERSION}}}",
            Version("1.2.3-p+a"),
            "11.22.33-pp+aa 1.2.3-p+a",
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
