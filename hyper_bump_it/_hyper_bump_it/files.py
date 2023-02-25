"""
Operation on files.
"""

from pathlib import Path

from . import format_pattern
from .config import File
from .error import FileGlobError, SearchTextNotFound
from .format_pattern import FormatContext, TextFormatter, keys
from .planned_changes import PlannedChange


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
    :raises SearchTextNotFound: A file did not contain the produced search text.
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
    file_data = file.read_bytes()
    file_text = file_data.decode()

    replace_text = formatter.format(replace_pattern, FormatContext.replace)
    search_text_maybe = formatter.format(search_pattern, FormatContext.search)

    if TextFormatter.is_used(keys.TODAY, search_text_maybe):
        # we need to convert the search text into a regex in order to match any date
        updated_text, no_replacement = _today_replace(
            search_text_maybe, file_text, replace_text
        )
    else:
        no_replacement = search_text_maybe not in file_text
        updated_text = file_text.replace(search_text_maybe, replace_text)

    if no_replacement:
        raise SearchTextNotFound(file.relative_to(project_root), search_pattern)

    return PlannedChange(
        file,
        project_root,
        old_content=file_text,
        new_content=updated_text,
        newline=PlannedChange.detect_line_ending(file_data),
    )


def _today_replace(
    partial_format_pattern: str,
    file_text: str,
    replace_text: str,
) -> tuple[str, bool]:
    # The first pass formatted all the keys except "today". Now, that is the only key to convert
    # into a regex pattern.
    match_pattern = format_pattern.create_matching_pattern(partial_format_pattern)
    updated_text, replace_count = match_pattern.subn(replace_text, file_text)
    return updated_text, replace_count == 0


def perform_change(change: PlannedChange) -> None:
    try:
        with change.file.open("w", newline=change.newline) as f:
            f.write(change.new_content)
    except FileNotFoundError:
        raise ValueError(
            f"Given file '{change.file}' does not exist. PlannedChange is not valid."
        )
