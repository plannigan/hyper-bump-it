"""
Use format patterns to produce regular expression matching patterns to determine the current
version from a keystone file.
"""
import re
from pathlib import Path
from re import Match, Pattern
from string import Formatter, Template
from typing import Optional

from semantic_version import Version

from hyper_bump_it._error import (
    FormatKeyError,
    FormatPatternError,
    IncompleteKeystoneVersionError,
    TodayFormatKeyError,
    VersionNotFound,
)
from hyper_bump_it._text_formatter import keys


def _version_regex(group_name: str) -> str:
    return rf"(?P<{group_name}>\d+\.\d+\.\d+(?:-[0-9a-zA-Z.-]+)?(?:\+[0-9a-zA-Z.-]+)?)"


def _number_part_regex(group_name: str) -> str:
    return rf"(?P<{group_name}>\d+)"


def _number_letter_part_regex(group_name: str) -> str:
    return rf"(?P<{group_name}>[0-9a-zA-Z.-]+)"


_MONTH_REGEX = r"(?:0[1-9]|1[0-2])"
_DAY_REGEX = r"(?:0[1-9]|[1-2]\d|3[0-1])"
_YEAR_REGEX = r"\d\d\d\d"
_TODAY_REGEX = rf"(?P<{keys.TODAY}>{_YEAR_REGEX}-{_MONTH_REGEX}-{_DAY_REGEX})"


_KEY_REPLACEMENT_REGEX = {
    keys.VERSION: _version_regex(keys.VERSION),
    keys.MAJOR: _number_part_regex(keys.MAJOR),
    keys.MINOR: _number_part_regex(keys.MINOR),
    keys.PATCH: _number_part_regex(keys.PATCH),
    keys.PRERELEASE: _number_letter_part_regex(keys.PRERELEASE),
    keys.BUILD: _number_letter_part_regex(keys.BUILD),
    keys.CURRENT_VERSION: _version_regex(keys.CURRENT_VERSION),
    keys.CURRENT_MAJOR: _number_part_regex(keys.CURRENT_MAJOR),
    keys.CURRENT_MINOR: _number_part_regex(keys.CURRENT_MINOR),
    keys.CURRENT_PATCH: _number_part_regex(keys.CURRENT_PATCH),
    keys.CURRENT_PRERELEASE: _number_letter_part_regex(keys.CURRENT_PRERELEASE),
    keys.CURRENT_BUILD: _number_letter_part_regex(keys.CURRENT_BUILD),
    keys.NEW_VERSION: _version_regex(keys.NEW_VERSION),
    keys.NEW_MAJOR: _number_part_regex(keys.NEW_MAJOR),
    keys.NEW_MINOR: _number_part_regex(keys.NEW_MINOR),
    keys.NEW_PATCH: _number_part_regex(keys.NEW_PATCH),
    keys.NEW_PRERELEASE: _number_letter_part_regex(keys.NEW_PRERELEASE),
    keys.NEW_BUILD: _number_letter_part_regex(keys.NEW_BUILD),
    keys.TODAY: _TODAY_REGEX,
}

_WEEK_OF_YEAR_REGEX = r"(?:[0-4]\d|5[0-3])"

_TODAY_REPLACEMENT_REGEX = {
    "w": r"[0-6]",
    "d": _DAY_REGEX,
    "m": _MONTH_REGEX,
    "y": r"\d\d",
    "Y": _YEAR_REGEX,
    "j": r"(?:[0-2]\d\d|3[0-5]\d|36[0-6])",
    "U": _WEEK_OF_YEAR_REGEX,
    "W": _WEEK_OF_YEAR_REGEX,
    "G": _YEAR_REGEX,
    "u": r"[1-7]",
    "V": _WEEK_OF_YEAR_REGEX,
}


def find_current_version(
    file: Path,
    search_pattern: str,
) -> Version:
    """
    Search a file for the version based on a given search pattern.

    :param file: File to read contents from.
    :param search_pattern: Format pattern to use for identifying the version.
    :return: Parsed version found in the file.
    :raises FormatError: There was an issue processing the keystone version using the search
        pattern.
    :raises VersionNotFound: None of the lines in the file matched the search pattern.
    """
    matching_pattern = _create_matching_pattern(search_pattern)
    for i, line in enumerate(file.read_text().splitlines()):
        if (match := matching_pattern.search(line)) is not None:
            version_string = _version_string_from_match(match)
            if version_string is None:
                raise IncompleteKeystoneVersionError(file, search_pattern)
            return Version(version_string)

    raise VersionNotFound(file, search_pattern)


def _create_matching_pattern(format_pattern: str) -> Pattern[str]:
    """
    Convert a format pattern into a regular expression pattern that can be used find the current
    version in a keystone file.

    :param format_pattern: Format pattern to be converted.
    :return: Regular expression pattern that will match the equivalent line.
    :raises FormatError: Format pattern was invalid or attempted to use an invalid key.
    """
    # We need the curtly brackets for the format operation. However, we will ensure they are
    # still escaped if they exist after the format.
    escaped_format_patter = (
        re.escape(format_pattern).replace("\\{", "{").replace("\\}", "}")
    )
    formatter = KeystoneFormatter()
    try:
        regex = formatter.vformat(
            escaped_format_patter, args=[], kwargs=_KEY_REPLACEMENT_REGEX
        )
    except KeyError:
        raise FormatKeyError(format_pattern, _KEY_REPLACEMENT_REGEX.keys())
    except ValueError as ex:
        raise FormatPatternError(format_pattern, str(ex))
    # none of the regular expressions from this module use curly brackets, so this is safe
    regex = regex.replace("{", "\\{").replace("}", "\\}")
    return re.compile(regex)


def _version_string_from_match(match: Match[str]) -> Optional[str]:
    # Work through the matched groups to rebuild the version data.
    # Prefer general keys to explicit current keys.
    # Ignore explicit new and extra keys
    groups = match.groupdict()
    # fast path for full version keys
    for version_key in (keys.VERSION, keys.CURRENT_VERSION):
        if (version_string := groups.get(version_key)) is not None:
            return version_string

    version_group_keys = {
        "major": (keys.MAJOR, keys.CURRENT_MAJOR),
        "minor": (keys.MINOR, keys.CURRENT_MINOR),
        "patch": (keys.PATCH, keys.CURRENT_PATCH),
        "prerelease": (keys.PRERELEASE, keys.CURRENT_PRERELEASE),
        "build": (keys.BUILD, keys.CURRENT_BUILD),
    }

    values: dict[str, str] = {}
    for version_part, part_keys in version_group_keys.items():
        for part_key in part_keys:
            if (part_value := groups.get(part_key)) is not None:
                values[version_part] = part_value
                break

    return _build_version(values)


def _build_version(values: dict[str, str]) -> Optional[str]:
    try:
        version_string = "{major}.{minor}.{patch}".format(
            major=values["major"],
            minor=values["minor"],
            patch=values["patch"],
        )
    except KeyError:
        return None

    if "prerelease" in values:
        version_string = f'{version_string}-{values["prerelease"]}'
    if "build" in values:
        version_string = f'{version_string}+{values["build"]}'
    return version_string


class KeystoneFormatter(Formatter):
    def format_field(self, value: str, format_spec: str) -> str:
        if value != _TODAY_REGEX or format_spec == "":
            # don't preform any format operations
            return value
        try:
            template = TodayTemplate(format_spec)
            result = template.substitute(_TODAY_REPLACEMENT_REGEX)
            return f"(?P<{keys.TODAY}>{result})"
        except (ValueError, KeyError):
            raise TodayFormatKeyError(format_spec, _TODAY_REPLACEMENT_REGEX.keys())

    def convert_field(self, value: str, conversion: Optional[str]) -> str:
        # don't preform any conversion operations
        return value


class TodayTemplate(Template):
    delimiter = "%"
