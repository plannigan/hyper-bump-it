from io import StringIO
from typing import Final, Literal

import pytest
import rich
from pytest_mock import MockerFixture
from typer import rich_utils as typer_rich_utils

# rich's line wrapping makes test cases that check output text tricky. By making the width very large, wrapping can be
# avoided. rich does check for a COLUMNS environment variable, but pytest also utilizes that variable, so using that
# affects pytest's output
FORCED_TERMINAL_WIDTH = 3000


@pytest.fixture
def capture_rich() -> StringIO:
    captured_text = StringIO()
    original_console_config = rich.get_console().__dict__
    rich.reconfigure(file=captured_text, width=FORCED_TERMINAL_WIDTH)
    try:
        yield captured_text
    finally:
        rich.get_console().__dict__ = original_console_config


@pytest.fixture(autouse=True)
def wide_terminal(mocker) -> None:
    # Patch Typer to use the forced width value.
    mocker.patch.object(typer_rich_utils, "MAX_WIDTH", FORCED_TERMINAL_WIDTH)
    mocker.patch.object(typer_rich_utils, "FORCE_TERMINAL", False)


class ForceInput:
    NO_INPUT: Final[Literal[""]] = ""

    def __init__(self, mocker: MockerFixture) -> None:
        self._mocker = mocker

    def __call__(self, text: str, *more: str) -> None:
        self._mocker.patch("builtins.input", side_effect=[text, *more])


@pytest.fixture
def force_input(mocker) -> ForceInput:
    yield ForceInput(mocker)
