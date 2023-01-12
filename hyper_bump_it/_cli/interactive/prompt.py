"""
Helper functionality for interactive prompts.
"""
from collections.abc import Mapping
from enum import Enum
from typing import Optional, TypeVar, cast

from rich.prompt import Prompt
from rich.text import Text

EnumT = TypeVar("EnumT", bound=Enum)


def enum_prompt(
    message: str,
    option_descriptions: Mapping[EnumT, str],
    default: EnumT,
) -> EnumT:
    enum_type = type(default)
    if set(enum_type) != option_descriptions.keys():
        missing_values: set[EnumT] = set(enum_type) - option_descriptions.keys()
        raise ValueError(
            f"Missing description for: {','.join(cast(str,x.value) for x in missing_values)}"
        )
    prompt_text = Text(message)
    prompt_text.append("\n")
    list_options(
        prompt_text,
        {
            option.value: description
            for option, description in option_descriptions.items()
        },
        cast(str, default.value),
    )
    prompt_text.append("Enter the option name")
    result_value = Prompt.ask(
        prompt_text,
        choices=[option.value for option in enum_type],
        show_choices=False,
        show_default=False,
        default=default.value,
    )
    return enum_type(result_value)


def list_options(
    text: Text, option_descriptions: Mapping[str, str], default: Optional[str] = None
) -> None:
    """
    Write the list of options and descriptions to the given text instance.

    :param text: Object to aggregate the text to be displayed
    :param option_descriptions: A set of options that can be selected paired with a description.
    :param default: Option that should include a default label. If `None`, no label will be added.
    """
    for option, description in option_descriptions.items():
        text.append(option, style="prompt.choices")
        text.append(f" - {description}")
        if option == default:
            text.append(" ")
            text.append("(default)", style="prompt.default")
        text.append("\n")
