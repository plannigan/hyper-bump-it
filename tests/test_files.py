from pathlib import Path

import pytest

from bump_it import _files as files
from bump_it._error import FileGlobError, VersionNotFound
from bump_it._files import FileConfig, PlannedChange
from bump_it._text_formatter import keys
from tests import sample_data as sd

SOME_FILE_NAME = "foo.txt"
SOME_OTHER_FILE_NAME = "bar.txt"

TEXT_FORMATTER = sd.some_text_formatter()


def test_collect_planned_changes__default_search_replace__planned_change_with_new_content(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        FileConfig(some_file.name),
        formatter=TEXT_FORMATTER,
    )

    assert len(changes) == 1
    assert changes[0] == PlannedChange(
        some_file,
        line_index=0,
        old_line=original_text,
        new_line=f"--{sd.SOME_OTHER_VERSION}--",
    )


def test_collect_planned_changes__custom_search_replace__planned_change_with_new_content(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_MAJOR}.{sd.SOME_MINOR}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        FileConfig(
            some_file.name,
            search_format_pattern=f"--{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}--",
            replace_format_pattern=f"--{{{keys.NEW_MAJOR}}}.{{{keys.NEW_MINOR}}}--",
        ),
        formatter=TEXT_FORMATTER,
    )

    assert len(changes) == 1
    assert changes[0] == PlannedChange(
        some_file,
        line_index=0,
        old_line=original_text,
        new_line=f"--{sd.SOME_OTHER_MAJOR}.{sd.SOME_OTHER_MINOR}--",
    )


def test_collect_planned_changes__match_later_in_file__planned_change_with_matching_line_index(
    tmp_path: Path,
):
    some_line_index = 2
    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text("\n" * some_line_index + original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        FileConfig(some_file.name),
        formatter=TEXT_FORMATTER,
    )

    assert len(changes) == 1
    assert changes[0] == PlannedChange(
        some_file,
        line_index=some_line_index,
        old_line=original_text,
        new_line=f"--{sd.SOME_OTHER_VERSION}--",
    )


def test_collect_planned_changes__multiple_files__planned_change_for_both(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    other_original_text = f"++{sd.SOME_VERSION}++"
    some_other_file = tmp_path / SOME_OTHER_FILE_NAME
    some_other_file.write_text(other_original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        FileConfig("*.txt"),
        formatter=TEXT_FORMATTER,
    )

    assert sorted(changes, key=lambda x: x.file) == [
        PlannedChange(
            some_other_file,
            line_index=0,
            old_line=other_original_text,
            new_line=f"++{sd.SOME_OTHER_VERSION}++",
        ),
        PlannedChange(
            some_file,
            line_index=0,
            old_line=original_text,
            new_line=f"--{sd.SOME_OTHER_VERSION}--",
        ),
    ]


def test_collect_planned_changes__version_not_found__error(tmp_path: Path):
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text("")

    with pytest.raises(VersionNotFound):
        files.collect_planned_changes(
            tmp_path,
            FileConfig(some_file.name),
            formatter=TEXT_FORMATTER,
        )


def test_collect_planned_changes__no_files_matched__error(tmp_path: Path):
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text("")

    with pytest.raises(FileGlobError):
        files.collect_planned_changes(
            tmp_path,
            FileConfig("non-existent.txt"),
            formatter=TEXT_FORMATTER,
        )
