"""
Operation on files.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bump_it._error import FileGlobError, VersionNotFound
from bump_it._text_formatter import TextFormatter, keys

DEFAULT_SEARCH_FORMAT_PATTERN = f"{{{keys.CURRENT_VERSION}}}"
DEFAULT_REPLACE_FORMAT_PATTERN = f"{{{keys.NEW_VERSION}}}"


@dataclass
class FileConfig:
    file_glob: str  # relative to project root directory
    search_format_pattern: Optional[str] = None
    replace_format_pattern: Optional[str] = None


@dataclass
class PlannedChange:
    file: Path  # including project root directory
    line_index: int
    old_line: str
    new_line: str


def collect_planned_changes(
    project_root: Path, config: FileConfig, formatter: TextFormatter
) -> list[PlannedChange]:
    """
    Aggregate a collection of changes that would occur across multiple files.

    :param project_root: Root directory to start looking for files.
    :param config: Configuration of how the changes should operate.
    :param formatter: Object that converts format patterns into text.
    :return: Descriptions of the change that would occur.
    :raises FileGlobError: Glob pattern for selecting files did not find any files.
    :raises VersionNotFound: A file did not contain the produced search text.
    """
    changes = [
        _planned_change_for(
            file, config.search_format_pattern, config.replace_format_pattern, formatter
        )
        for file in project_root.glob(config.file_glob)
    ]
    if not changes:
        raise FileGlobError(project_root, config.file_glob)
    return changes


def _planned_change_for(
    file: Path,
    search_pattern: Optional[str],
    replace_pattern: Optional[str],
    formatter: TextFormatter,
) -> PlannedChange:

    search_pattern = search_pattern or DEFAULT_SEARCH_FORMAT_PATTERN
    replace_pattern = replace_pattern or DEFAULT_REPLACE_FORMAT_PATTERN
    search_text = formatter.format(search_pattern)
    for i, line in enumerate(file.read_text().splitlines()):
        if search_text in line:
            replace_text = formatter.format(replace_pattern)
            return PlannedChange(
                file,
                line_index=i,
                old_line=line,
                new_line=line.replace(search_text, replace_text),
            )

    raise VersionNotFound(file, search_pattern)
