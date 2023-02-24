"""
Convert a search pattern into a regex pattern.
"""
import re
from re import Pattern
from string import Formatter, Template
from typing import Optional

from ..error import FormatKeyError, FormatPatternError, TodayFormatKeyError
from . import keys


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


def create_matching_pattern(format_pattern: str) -> Pattern[str]:
    """
    Convert a format pattern into a regular expression pattern that can be used find the current
    version in a keystone file.

    :param format_pattern: Format pattern to be converted.
    :return: Regular expression pattern that will match the equivalent line.
    :raises FormatError: Format pattern was invalid or attempted to use an invalid key.
    """
    # We need the curly brackets for the format operation. However, we will ensure they are
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


class KeystoneFormatter(Formatter):
    def format_field(self, value: str, format_spec: str) -> str:
        if value != _TODAY_REGEX or format_spec == "":
            # don't preform any format operations
            return value
        try:
            template = TodayTemplate(format_spec)
            result = template.substitute(_TODAY_REPLACEMENT_REGEX)
        except (ValueError, KeyError):
            raise TodayFormatKeyError(format_spec, _TODAY_REPLACEMENT_REGEX.keys())
        return f"(?P<{keys.TODAY}>{result})"

    def convert_field(self, value: str, conversion: Optional[str]) -> str:
        # don't preform any conversion operations
        return value


class TodayTemplate(Template):
    delimiter = "%"
