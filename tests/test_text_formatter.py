import re
from datetime import date

import pytest
from semantic_version import Version

from bump_it._error import FormatKeyError, FormatPatternError
from bump_it._text_formatter import TextFormatter, keys

ALL_KEYS = tuple(name for name in dir(keys) if not name.startswith("__"))

SOME_DATE = date(year=2022, month=10, day=19)
SOME_MAJOR = 1
SOME_MINOR = 2
SOME_PATCH = 3
SOME_PRERELEASE = "11.22"
SOME_BUILD = "b123.321"
SOME_VERSION = Version(
    major=SOME_MAJOR,
    minor=SOME_MINOR,
    patch=SOME_PATCH,
    prerelease=SOME_PRERELEASE.split("."),
    build=SOME_BUILD.split("."),
)
SOME_OTHER_MAJOR = 4
SOME_OTHER_MINOR = 5
SOME_OTHER_PATCH = 6
SOME_OTHER_PRERELEASE = "33.44"
SOME_OTHER_BUILD = "b456.654"
SOME_OTHER_VERSION = Version(
    major=SOME_OTHER_MAJOR,
    minor=SOME_OTHER_MINOR,
    patch=SOME_OTHER_PATCH,
    prerelease=SOME_OTHER_PRERELEASE.split("."),
    build=SOME_OTHER_BUILD.split("."),
)
SOME_OTHER_PARTIAL_VERSION = Version(
    major=SOME_OTHER_MAJOR,
    minor=SOME_OTHER_MINOR,
    patch=SOME_OTHER_PATCH,
)
TEXT_FORMATTER = TextFormatter(
    current_version=SOME_VERSION, new_version=SOME_OTHER_VERSION, today=SOME_DATE
)


@pytest.mark.parametrize(
    ["key", "expected_value"],
    [
        (keys.CURRENT_VERSION, str(SOME_VERSION)),
        (keys.CURRENT_MAJOR, str(SOME_MAJOR)),
        (keys.CURRENT_MINOR, str(SOME_MINOR)),
        (keys.CURRENT_PATCH, str(SOME_PATCH)),
        (keys.CURRENT_PRERELEASE, SOME_PRERELEASE),
        (keys.CURRENT_BUILD, SOME_BUILD),
        (keys.NEW_VERSION, str(SOME_OTHER_VERSION)),
        (keys.NEW_MAJOR, str(SOME_OTHER_MAJOR)),
        (keys.NEW_MINOR, str(SOME_OTHER_MINOR)),
        (keys.NEW_PATCH, str(SOME_OTHER_PATCH)),
        (keys.NEW_PRERELEASE, SOME_OTHER_PRERELEASE),
        (keys.NEW_BUILD, SOME_OTHER_BUILD),
        (keys.TODAY, str(SOME_DATE)),
    ],
)
def test_format__replace_versions__new_version(key: str, expected_value: str):
    result = TEXT_FORMATTER.format(f"--{{{key}}}--")
    assert result == f"--{expected_value}--"


def test_format__today__supported_with_formatters():
    result = TEXT_FORMATTER.format(f"--{{{keys.TODAY}:%B %d, %Y}}--")
    assert result == "--October 19, 2022--"


def test_format__use_optional_keys_for_version_without_values__empty_string_inserted():
    text_formatter = TextFormatter(
        SOME_VERSION, SOME_OTHER_PARTIAL_VERSION, today=SOME_DATE
    )

    result = text_formatter.format(
        f"--{{{keys.NEW_PRERELEASE}}}__{{{keys.NEW_BUILD}}}--"
    )
    assert result == "--__--"


@pytest.mark.parametrize("key", ALL_KEYS)
def test_format__each_key__valid_result(key: str):
    # ensure that each key is usable & we didn't forget to add an explicit test case
    result = TEXT_FORMATTER.format(f"--{{{getattr(keys, key)}}}--")
    assert re.match("^--.+-$", result)


def test_format__invalid_pattern__error():
    with pytest.raises(FormatPatternError):
        TEXT_FORMATTER.format("--{--")


def test_format__invalid_key__error():
    with pytest.raises(FormatKeyError):
        TEXT_FORMATTER.format("--{SOME_NOT_VALID_KEY}--")
