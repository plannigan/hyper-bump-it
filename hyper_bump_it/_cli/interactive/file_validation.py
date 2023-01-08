"""
Validate a file definition to see if it could be used for a specific project.
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional

from semantic_version import Version

from hyper_bump_it._config import FileDefinition
from hyper_bump_it._error import FormatError
from hyper_bump_it._text_formatter import FormatContext, TextFormatter

_FAKE_NEXT_VERSION = Version("1.2.3")


class FailureType(Enum):
    NoFiles = auto()
    KeystoneMultipleFiles = auto()
    BadSearchPattern = auto()
    BadReplacePattern = auto()
    SearchPatternNotFound = auto()


@dataclass
class ValidationFailure:
    failure_type: FailureType
    description: str


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
            return ValidationFailure(FailureType.BadSearchPattern, str(ex))

        if definition.replace_format_pattern is not None:
            try:
                self._text_formatter.format(
                    definition.replace_format_pattern, context=FormatContext.replace
                )
            except FormatError as ex:
                return ValidationFailure(FailureType.BadReplacePattern, str(ex))
        return self._check_file_contents(search_text, matched_files)

    def _validate_matched_files(
        self, definition: FileDefinition, matched_files: list[Path]
    ) -> Optional[ValidationFailure]:
        if len(matched_files) == 0:
            return ValidationFailure(
                FailureType.NoFiles,
                f"'{definition.file_glob}' did not match any files in the project root: {self._project_root}",
            )
        if definition.keystone and len(matched_files) != 1:
            file_names = "', '".join(str(file) for file in matched_files)
            return ValidationFailure(
                FailureType.KeystoneMultipleFiles,
                f"Keystone files can only match one file. '{definition.file_glob}' matched: '{file_names}'",
            )
        return None

    @staticmethod
    def _check_file_contents(
        search_text: str, matched_files: list[Path]
    ) -> Optional[ValidationFailure]:
        for file in matched_files:
            if search_text not in file.read_text():
                return ValidationFailure(
                    FailureType.SearchPatternNotFound,
                    f"The search text '{search_text}' was not found in matched file '{file}'",
                )
        return None
