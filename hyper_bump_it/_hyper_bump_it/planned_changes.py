"""
Low level primitives for file interactions.
"""
import difflib
from dataclasses import InitVar, dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Optional

_LINE_FEED = b"\n"[0]
_CARRIAGE_RETURN = b"\r"[0]


@dataclass
class PlannedChange:
    file: Path  # absolute resolved path
    project_root: InitVar[Path]  # absolute resolved path
    relative_file: Path = field(init=False)
    old_content: str
    new_content: str
    newline: Optional[str]

    def __post_init__(self, project_root: Path) -> None:
        self.relative_file = self.file.relative_to(project_root)

    @cached_property
    def change_diff(self) -> str:
        """
        Unified diff text for the intended change.
        """
        relative_file_str = str(self.relative_file)
        return "".join(
            difflib.unified_diff(
                self.old_content.splitlines(keepends=True),
                self.new_content.splitlines(keepends=True),
                fromfile=relative_file_str,
                tofile=relative_file_str,
            )
        )

    @staticmethod
    def detect_line_ending(data: bytes) -> Optional[str]:
        """
        Attempt to determine the line ending used within a file.

        :param data: Binary content of the file.
        :return: New line character sequence for the file. `None` if no new line characters are
            found.
        """
        cr_found = False
        for byte in data:
            if byte == _CARRIAGE_RETURN:
                cr_found = True
            elif byte == _LINE_FEED:
                return "\r\n" if cr_found else "\n"
        # no trailing new line
        return None
