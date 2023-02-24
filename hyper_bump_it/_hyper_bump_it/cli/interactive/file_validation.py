"""
Validate a file definition to see if it could be used for a specific project.
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional

from rich.text import Text

from ... import ui
from ...config import FileDefinition
from ...error import FormatError
from ...format_pattern import FormatContext, TextFormatter
from ...version import Version

_FAKE_NEXT_VERSION = Version(1, 2, 3)


class FailureType(Enum):
    NoFiles = auto()
    KeystoneMultipleFiles = auto()
    BadSearchPattern = auto()
    BadReplacePattern = auto()
    SearchPatternNotFound = auto()


@dataclass
class ValidationFailure:
    failure_type: FailureType
    description: Text


class DefinitionValidator:
    def __init__(self, current_version: Version, project_root: Path) -> None:
        self._project_root = project_root
        self._text_formatter = TextFormatter(
            current_version=current_version, new_version=_FAKE_NEXT_VERSION
        )

    def __call__(self, definition: FileDefinition) -> Optional[ValidationFailure]:
        matched_files = list(self._project_root.glob(definition.file_glob))
        if (
            result := self._validate_matched_files(definition, matched_files)
        ) is not None:
            return result

        try:
            search_text = self._text_formatter.format(
                definition.search_format_pattern, context=FormatContext.search
            )
        except FormatError as ex:
            return ValidationFailure(FailureType.BadSearchPattern, Text(str(ex)))

        if definition.replace_format_pattern is not None:
            try:
                self._text_formatter.format(
                    definition.replace_format_pattern, context=FormatContext.replace
                )
            except FormatError as ex:
                return ValidationFailure(FailureType.BadReplacePattern, Text(str(ex)))
        return self._check_file_contents(search_text, matched_files)

    def _validate_matched_files(
        self, definition: FileDefinition, matched_files: list[Path]
    ) -> Optional[ValidationFailure]:
        if len(matched_files) == 0:
            return ValidationFailure(
                FailureType.NoFiles,
                Text("'")
                .append(definition.file_glob, style="file.glob")
                .append("' did not match any files in the project root: ")
                .append(str(self._project_root), style="file.path"),
            )
        if definition.keystone and len(matched_files) != 1:
            message = Text("Keystone files can only match one file. '")
            message.append(definition.file_glob, style="file.glob")
            message.append("' matched: ")
            message.append_text(
                ui.list_styled_values(
                    (
                        str(file.relative_to(self._project_root))
                        for file in matched_files
                    ),
                    style="file.path",
                    quoted=True,
                )
            )
            return ValidationFailure(FailureType.KeystoneMultipleFiles, message)
        return None

    @staticmethod
    def _check_file_contents(
        search_text: str, matched_files: list[Path]
    ) -> Optional[ValidationFailure]:
        for file in matched_files:
            if search_text not in file.read_text():
                return ValidationFailure(
                    FailureType.SearchPatternNotFound,
                    Text("The search text '")
                    .append(search_text, style="format.text")
                    .append("' was not found in matched file '")
                    .append(str(file), style="file.path")
                    .append("'"),
                )
        return None
