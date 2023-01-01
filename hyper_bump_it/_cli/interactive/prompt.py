"""
Helper functionality for interactive prompts.
"""
from enum import Enum
from typing import TypeVar, cast

from rich.prompt import Prompt, PromptBase
from rich.text import Text
from semantic_version import Version

EnumT = TypeVar("EnumT", bound=Enum)


def enum_prompt(
    message: str,
    option_descriptions: dict[EnumT, str],
    default: EnumT,
) -> EnumT:
    enum_type = type(default)
    if set(enum_type) != option_descriptions.keys():
        missing_values: set[EnumT] = set(enum_type) - option_descriptions.keys()
        raise ValueError(
            f"Missing description for: {','.join(x.value for x in missing_values)}"
        )
    prompt_text = Text(message)
    prompt_text.append("\n")
    for option, description in option_descriptions.items():
        prompt_text.append(cast(str, option.value), style="prompt.choices")
        prompt_text.append(f" - {description}")
        if option == default:
            prompt_text.append(" ")
            prompt_text.append("(default)", style="prompt.default")
        prompt_text.append("\n")
    prompt_text.append("Enter the option name")
    result_value = Prompt.ask(
        prompt_text,
        choices=[option.value for option in enum_type],
        show_choices=False,
        show_default=False,
        default=default.value,
    )
    return enum_type(result_value)


class VersionPrompt(PromptBase[Version]):
    response_type = Version
