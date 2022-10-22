"""
Common test data that can be used across multiple test cases.
"""
from datetime import date

from semantic_version import Version

from bump_it._text_formatter import TextFormatter

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


def some_text_formatter(
    current_version: Version = SOME_VERSION,
    new_version: Version = SOME_OTHER_VERSION,
    today: date = SOME_DATE,
) -> TextFormatter:
    return TextFormatter(current_version, new_version, today)
