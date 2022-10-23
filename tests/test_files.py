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


def test_collect_planned_changes__only_search__planned_change_with_new_content(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_VERSION}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        FileConfig(some_file.name, search_format_pattern=f"--{{{keys.VERSION}}}--"),
        formatter=TEXT_FORMATTER,
    )

    assert len(changes) == 1
    assert changes[0] == PlannedChange(
        some_file,
        line_index=0,
        old_line=original_text,
        new_line=f"--{sd.SOME_OTHER_VERSION}--",
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


@pytest.mark.parametrize(
    "line_ending",
    [
        "",
        "\n",
        "\r\n",
    ],
)
def test_perform_change__single_line_file__file_updated_proper_end(
    line_ending: str, tmp_path: Path
):
    original_text = f"--{sd.SOME_VERSION}--"
    replacement_text = f"--{sd.SOME_OTHER_VERSION}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_bytes(f"{original_text}{line_ending}".encode())

    files.perform_change(
        PlannedChange(
            some_file, line_index=0, old_line=original_text, new_line=replacement_text
        )
    )

    expected = f"{replacement_text}{line_ending}".encode()
    assert some_file.read_bytes() == expected


@pytest.mark.parametrize(
    "line_ending",
    [
        "\n",
        "\r\n",
    ],
)
def test_perform_change__multi_line_file__file_updated_proper_end(
    line_ending: str, tmp_path: Path
):
    leading_line = "hello"
    trailing_line = "goodbye"

    def _create_content(center_line: str) -> bytes:
        return line_ending.join([leading_line, center_line, trailing_line]).encode()

    original_text = f"--{sd.SOME_VERSION}--"
    replacement_text = f"--{sd.SOME_OTHER_VERSION}--"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_bytes(_create_content(original_text))

    files.perform_change(
        PlannedChange(
            some_file, line_index=1, old_line=original_text, new_line=replacement_text
        )
    )

    expected = _create_content(replacement_text)
    assert some_file.read_bytes() == expected


def test_perform_change__invalid_file__error(tmp_path: Path):
    some_non_existent_file = tmp_path / SOME_FILE_NAME
    original_text = f"--{sd.SOME_VERSION}--"
    replacement_text = f"--{sd.SOME_OTHER_VERSION}--"

    with pytest.raises(ValueError):
        files.perform_change(
            PlannedChange(
                some_non_existent_file,
                line_index=0,
                old_line=original_text,
                new_line=replacement_text,
            )
        )


def test_perform_change__invalid_line_index__error(tmp_path: Path):
    some_too_large_index = 100000
    some_file = tmp_path / SOME_FILE_NAME
    original_text = f"--{sd.SOME_VERSION}--"
    replacement_text = f"--{sd.SOME_OTHER_VERSION}--"
    some_file.write_bytes(f"{original_text}\n".encode())

    with pytest.raises(ValueError):
        files.perform_change(
            PlannedChange(
                some_file,
                line_index=some_too_large_index,
                old_line=original_text,
                new_line=replacement_text,
            )
        )
