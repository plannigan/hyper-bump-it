from enum import Enum
from io import StringIO

import pytest

from hyper_bump_it._cli.interactive import prompt
from tests.conftest import ForceInput


class Options(Enum):
    Foo = "foo"
    Bar = "bar"


SOME_PROMPT_TEXT = "test text prompt"
SOME_DESCRIPTION = "a test description"
SOME_OTHER_DESCRIPTION = "a different test description"
SOME_OPTION = Options.Bar
SOME_OTHER_OPTION = Options.Bar
SOME_NON_OPTION_VALUE = "not an option value"


def test_enum_prompt__no_response__default(force_input: ForceInput):
    force_input(force_input.NO_INPUT)

    result = prompt.enum_prompt(
        SOME_PROMPT_TEXT,
        {
            Options.Foo: SOME_DESCRIPTION,
            Options.Bar: SOME_OTHER_DESCRIPTION,
        },
        SOME_OPTION,
    )

    assert result == SOME_OPTION


def test_enum_prompt__invalid_valid__valid_response(force_input: ForceInput):
    force_input(SOME_NON_OPTION_VALUE, SOME_OPTION.value)

    result = prompt.enum_prompt(
        SOME_PROMPT_TEXT,
        {
            Options.Foo: SOME_DESCRIPTION,
            Options.Bar: SOME_OTHER_DESCRIPTION,
        },
        SOME_OTHER_OPTION,
    )

    assert result == SOME_OPTION


def test_enum_prompt__missing_option_description__error():
    with pytest.raises(ValueError):
        prompt.enum_prompt(
            SOME_PROMPT_TEXT,
            {
                Options.Bar: SOME_OTHER_DESCRIPTION,
            },
            SOME_OPTION,
        )


def test_enum_prompt__expected_output(force_input: ForceInput, capture_rich: StringIO):
    force_input(force_input.NO_INPUT)
    prompt.enum_prompt(
        SOME_PROMPT_TEXT,
        {
            Options.Foo: SOME_DESCRIPTION,
            Options.Bar: SOME_OTHER_DESCRIPTION,
        },
        SOME_OPTION,
    )

    assert (
        capture_rich.getvalue() == f"{SOME_PROMPT_TEXT}\n"
        f"{Options.Foo.value} - {SOME_DESCRIPTION}\n"
        f"{Options.Bar.value} - {SOME_OTHER_DESCRIPTION} (default)\n"
        f"Enter the option name: "
    )
