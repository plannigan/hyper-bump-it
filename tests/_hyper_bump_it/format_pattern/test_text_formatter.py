import re

import pytest

from hyper_bump_it._hyper_bump_it.error import FormatKeyError, FormatPatternError
from hyper_bump_it._hyper_bump_it.format_pattern import (
    FormatContext,
    TextFormatter,
    keys,
)
from tests._hyper_bump_it import sample_data as sd

TEXT_FORMATTER = sd.some_text_formatter()


@pytest.mark.parametrize(
    ["key", "expected_value"],
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
        (keys.TODAY, str(sd.SOME_DATE)),
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
        sd.SOME_VERSION, sd.SOME_OTHER_PARTIAL_VERSION, today=sd.SOME_DATE
    )

    result = text_formatter.format(
        f"--{{{keys.NEW_PRERELEASE}}}__{{{keys.NEW_BUILD}}}--"
    )
    assert result == "--__--"


@pytest.mark.parametrize(
    ["context", "key", "expected_value"],
    [
        (FormatContext.search, keys.VERSION, str(sd.SOME_VERSION)),
        (FormatContext.search, keys.MAJOR, str(sd.SOME_MAJOR)),
        (FormatContext.search, keys.MINOR, str(sd.SOME_MINOR)),
        (FormatContext.search, keys.PATCH, str(sd.SOME_PATCH)),
        (FormatContext.search, keys.PRERELEASE, sd.SOME_PRERELEASE),
        (FormatContext.search, keys.BUILD, sd.SOME_BUILD),
        (FormatContext.replace, keys.VERSION, str(sd.SOME_OTHER_VERSION)),
        (FormatContext.replace, keys.MAJOR, str(sd.SOME_OTHER_MAJOR)),
        (FormatContext.replace, keys.MINOR, str(sd.SOME_OTHER_MINOR)),
        (FormatContext.replace, keys.PATCH, str(sd.SOME_OTHER_PATCH)),
        (FormatContext.replace, keys.PRERELEASE, sd.SOME_OTHER_PRERELEASE),
        (FormatContext.replace, keys.BUILD, sd.SOME_OTHER_BUILD),
    ],
)
def test_format__specified_context__respective_version(
    context: FormatContext, key: str, expected_value: str
):
    result = TEXT_FORMATTER.format(f"--{{{key}}}--", context)
    assert result == f"--{expected_value}--"


@pytest.mark.parametrize("key", sd.ALL_KEYS)
def test_format__each_key__valid_result(key: str):
    # ensure that each key is usable & we didn't forget to add an explicit test case
    result = TEXT_FORMATTER.format(f"--{{{key}}}--", context=FormatContext.search)
    assert re.match("^--.+-$", result)


def test_format__invalid_pattern__error():
    with pytest.raises(FormatPatternError):
        TEXT_FORMATTER.format("--{--")


@pytest.mark.parametrize("key_name", ["SOME_NOT_VALID_KEY", "123", ""])
def test_format__invalid_key__error(key_name):
    with pytest.raises(FormatKeyError):
        TEXT_FORMATTER.format(f"--{{{key_name}}}--")


@pytest.mark.parametrize(
    ["key", "format_pattern", "expected_result"],
    [
        (keys.VERSION, f"{{{keys.VERSION}}}", True),
        (keys.TODAY, f"{{{keys.TODAY}}}", True),
        (keys.TODAY, f"{{{keys.TODAY}:%Y-%m-%d}}", True),
        (keys.TODAY, f"{{{keys.VERSION}}}", False),
        (keys.TODAY, "", False),
        (keys.TODAY, "{}", False),
        (keys.TODAY, "{0}", False),
    ],
)
def test_is_used___expected_output(key, format_pattern, expected_result):
    result = TextFormatter.is_used(key, format_pattern)
    assert result == expected_result
