from io import StringIO

import pytest
import rich
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
