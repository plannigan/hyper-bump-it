"""
Display interface for working with rich.
"""
from collections.abc import Iterable, Mapping
from enum import Enum
from typing import Optional, TypeVar, Union, cast, overload

from rich import prompt
from rich.align import AlignMethod
from rich.console import Console, RichCast
from rich.panel import Panel
from rich.rule import Rule
from rich.style import Style, StyleType
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

from .compat import LiteralString, TypeAlias

TextType: TypeAlias = Union[Text, LiteralString]
PanelMessage: TypeAlias = Union[RichCast, str]

_DISPLAY_THEME = Theme(
    styles={
        "app": Style(color="green"),
        "valid": Style(color="green"),
        "invalid": Style(color="red", bold=True),
        "emphasis": Style(bold=True),
        "error.msg": Style(color="red"),
        "error.loc": Style(color="cyan"),
        "file.path": Style(color="bright_blue", bold=True),
        "file.glob": Style(color="deep_sky_blue1"),
        "format.pattern": Style(color="orange4"),
        "format.text": Style(color="orange4"),
        "patch.old": Style(color="red"),
        "patch.new": Style(color="green"),
        "vcs.branch": Style(color="cyan", bold=True),
        "vcs.commit": Style(color="magenta", bold=True),
        "vcs.tag": Style(color="cyan", bold=True),
        "vcs.remote": Style(color="dark_green", bold=True),
        "vcs.action": Style(color="green", bold=True),
        "prompt.choices": Style(color="magenta", bold=True),
        "prompt.default": Style(color="cyan", bold=True),
    },
    inherit=False,
)

_CONSOLE = Console(theme=_DISPLAY_THEME, highlight=False)


def blank_line() -> None:
    _CONSOLE.print()


def display(message: Optional[TextType]) -> None:
    _CONSOLE.print(message)


def rule(message: TextType) -> None:
    _CONSOLE.print(Rule(title=message))


def panel(
    message: PanelMessage,
    border_style: StyleType,
    title: Optional[TextType],
    title_align: AlignMethod = "left",
) -> None:
    _CONSOLE.print(
        Panel(message, title=title, title_align=title_align, border_style=border_style)
    )


@overload
def ask(message: TextType, *, default: str = ...) -> str:
    ...


@overload
def ask(message: TextType, *, default: None) -> Optional[str]:
    ...


def ask(message: TextType, *, default: Optional[str] = None) -> Optional[str]:
    return prompt.Prompt.ask(
        message, default=default, show_default=False, console=_CONSOLE
    )


def confirm(message: TextType, default: bool) -> bool:
    return prompt.Confirm.ask(message, default=default, console=_CONSOLE)


class _Sentinel(Enum):
    A = 0


T = TypeVar("T")
_NOT_GIVEN = _Sentinel.A


@overload
def choice(
    message: Text, *, choices: list[str], default: str = ..., show_choices: bool = False
) -> str:
    ...


@overload
def choice(
    message: Text, *, choices: list[str], default: None, show_choices: bool = False
) -> Optional[str]:
    ...


def choice(
    message: Text,
    *,
    choices: list[str],
    default: Union[Optional[str], _Sentinel] = _NOT_GIVEN,
    show_choices: bool = False,
) -> Optional[str]:
    if isinstance(default, _Sentinel):
        return prompt.Prompt.ask(
            message,
            choices=choices,
            show_choices=show_choices,
            show_default=False,
            console=_CONSOLE,
        )

    return prompt.Prompt.ask(
        message,
        choices=choices,
        default=default,
        show_choices=show_choices,
        show_default=False,
        console=_CONSOLE,
    )


def choice_int(
    message: Text,
    *,
    choices: list[str],
) -> int:
    return prompt.IntPrompt.ask(
        message,
        choices=choices,
        show_choices=False,
        show_default=False,
        console=_CONSOLE,
    )


EnumT = TypeVar("EnumT", bound=Enum)


def choice_enum(
    message: TextType,
    option_descriptions: Mapping[EnumT, TextType],
    default: EnumT,
) -> EnumT:
    enum_type = type(default)
    default_value = cast(str, default.value)
    all_enum_values: set[EnumT] = set(enum_type)
    if all_enum_values != option_descriptions.keys():
        missing_values = all_enum_values - option_descriptions.keys()
        raise ValueError(
            f"Missing description for: {','.join(cast(str, x.value) for x in missing_values)}"
        )
    prompt_text = message if isinstance(message, Text) else Text(message)
    prompt_text.append("\n")
    prompt_text.append_text(
        list_options(
            {
                option.value: description
                for option, description in option_descriptions.items()
            },
            default_value,
        )
    )
    prompt_text.append("Enter the option name")
    result_value = choice(
        prompt_text,
        choices=[option.value for option in enum_type],
        default=default_value,
    )
    return enum_type(result_value)


def display_diff(diff_text: str) -> None:
    syntax = Syntax(diff_text, "udiff", background_color="default")
    _CONSOLE.print(syntax)


def list_options(
    option_descriptions: Mapping[str, TextType],
    default: Optional[str] = None,
) -> Text:
    """
    Write the list of options and descriptions to the given text instance.

    :param option_descriptions: A set of options that can be selected paired with a description.
    :param default: Option that should include a default label. If `None`, no label will be added.
    """
    message = Text()
    for option, description in option_descriptions.items():
        message.append(option, style="prompt.choices")
        message.append(" - ")
        message.append(description)
        if option == default:
            message.append(" ")
            message.append("(default)", style="prompt.default")
        message.append("\n")
    return message


def list_styled_values(values: Iterable[str], style: str, quoted: bool = False) -> Text:
    quote = "'" if quoted else ""
    return Text.assemble(
        quote,
        Text(f"{quote}, {quote}").join(Text(value, style=style) for value in values),
        quote,
    )
