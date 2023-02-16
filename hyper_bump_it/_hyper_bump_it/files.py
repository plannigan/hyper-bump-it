"""
Operation on files.
"""

from pathlib import Path

from .config import File
from .error import FileGlobError, VersionNotFound
from .planned_changes import PlannedChange
from .text_formatter import TextFormatter
from .text_formatter.text_formatter import FormatContext


def collect_planned_changes(
    project_root: Path, config: File, formatter: TextFormatter
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
            file,
            config.search_format_pattern,
            config.replace_format_pattern,
            formatter,
            project_root,
        )
        for file in project_root.glob(config.file_glob)
    ]
    if not changes:
        raise FileGlobError(project_root, config.file_glob)
    return changes


def _planned_change_for(
    file: Path,
    search_pattern: str,
    replace_pattern: str,
    formatter: TextFormatter,
    project_root: Path,
) -> PlannedChange:
    search_text = formatter.format(search_pattern, FormatContext.search)

    file_data = file.read_bytes()
    file_text = file_data.decode()
    updated_text = file_text.replace(
        search_text, formatter.format(replace_pattern, FormatContext.replace)
    )
    if updated_text == file_text:
        raise VersionNotFound(file.relative_to(project_root), search_pattern)

    return PlannedChange(
        file,
        project_root,
        old_content=file_text,
        new_content=updated_text,
        newline=PlannedChange.detect_line_ending(file_data),
    )


def perform_change(change: PlannedChange) -> None:
    try:
        with change.file.open("w", newline=change.newline) as f:
            f.write(change.new_content)
    except FileNotFoundError:
        raise ValueError(
            f"Given file '{change.file}' does not exist. PlannedChange is not valid."
        )
