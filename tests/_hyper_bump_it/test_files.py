import os
from pathlib import Path
from textwrap import dedent
from typing import Optional

import pytest

from hyper_bump_it._hyper_bump_it import files
from hyper_bump_it._hyper_bump_it.error import FileGlobError, VersionNotFound
from hyper_bump_it._hyper_bump_it.files import PlannedChange
from hyper_bump_it._hyper_bump_it.text_formatter import keys
from tests._hyper_bump_it import sample_data as sd

SOME_FILE_NAME = "foo.txt"
SOME_OTHER_FILE_NAME = "bar.txt"

TEXT_FORMATTER = sd.some_text_formatter()


@pytest.mark.parametrize(
    ["old_content", "new_content", "expected_diff"],
    [
        (
            sd.SOME_OLD_LINE,
            sd.SOME_NEW_LINE,
            dedent(
                f"""\
    --- {sd.SOME_GLOB_MATCHED_FILE_NAME}
    +++ {sd.SOME_GLOB_MATCHED_FILE_NAME}
    @@ -1 +1 @@
    -start text+updated text"""
            ),
        ),
        (
            sd.SOME_FILE_CONTENT,
            sd.SOME_OTHER_FILE_CONTENT,
            dedent(
                f"""\
    --- {sd.SOME_GLOB_MATCHED_FILE_NAME}
    +++ {sd.SOME_GLOB_MATCHED_FILE_NAME}
    @@ -1,2 +1,2 @@
    ---1.2.3-11.22+b123.321--
    +--4.5.6-33.44+b456.654--
     abc"""
            ),
        ),
    ],
)
def test_planned_change_diff__expected_output(old_content, new_content, expected_diff):
    planned_change = PlannedChange(
        sd.SOME_ABSOLUTE_DIRECTORY / sd.SOME_GLOB_MATCHED_FILE_NAME,
        sd.SOME_ABSOLUTE_DIRECTORY,
        old_content,
        new_content,
        "\n",
    )

    assert planned_change.change_diff == expected_diff


@pytest.mark.parametrize(
    ["original_text", "expected_text", "newline"],
    [
        (f"--{sd.SOME_VERSION}--", f"--{sd.SOME_OTHER_VERSION}--", None),
        (f"\n\n--{sd.SOME_VERSION}--", f"\n\n--{sd.SOME_OTHER_VERSION}--", "\n"),
        (
            f"--{sd.SOME_VERSION}-- --{sd.SOME_VERSION}--",
            f"--{sd.SOME_OTHER_VERSION}-- --{sd.SOME_OTHER_VERSION}--",
            None,
        ),
    ],
)
def test_collect_planned_changes__default_search_replace_single_line__planned_change_with_new_content(
    original_text,
    expected_text,
    newline,
    tmp_path: Path,
):
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        sd.some_file(some_file.name),
        formatter=TEXT_FORMATTER,
    )

    assert changes == [
        PlannedChange(
            file=some_file,
            project_root=tmp_path,
            old_content=original_text,
            new_content=expected_text,
            newline=newline,
        )
    ]


def test_collect_planned_changes__multi_occurrence__multiple_planned_change_with_new_content(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_VERSION}--\n\n++{sd.SOME_VERSION}++"
    new_text = f"--{sd.SOME_OTHER_VERSION}--\n\n++{sd.SOME_OTHER_VERSION}++"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        sd.some_file(some_file.name),
        formatter=TEXT_FORMATTER,
    )

    assert changes == [
        PlannedChange(
            file=some_file,
            project_root=tmp_path,
            old_content=original_text,
            new_content=new_text,
            newline="\n",
        ),
    ]


def test_collect_planned_changes__custom_search_replace__planned_change_with_new_content(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_MAJOR}.{sd.SOME_MINOR}--\n"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        sd.some_file(
            some_file.name,
            search_format_pattern=f"--{{{keys.CURRENT_MAJOR}}}.{{{keys.CURRENT_MINOR}}}--",
            replace_format_pattern=f"--{{{keys.NEW_MAJOR}}}.{{{keys.NEW_MINOR}}}--",
        ),
        formatter=TEXT_FORMATTER,
    )

    assert changes == [
        PlannedChange(
            file=some_file,
            project_root=tmp_path,
            old_content=original_text,
            new_content=f"--{sd.SOME_OTHER_MAJOR}.{sd.SOME_OTHER_MINOR}--\n",
            newline="\n",
        )
    ]


def test_collect_planned_changes__multiple_files__planned_change_for_both(
    tmp_path: Path,
):
    original_text = f"--{sd.SOME_VERSION}--\n"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)

    other_original_text = f"++{sd.SOME_VERSION}++"
    some_other_file = tmp_path / SOME_OTHER_FILE_NAME
    some_other_file.write_text(other_original_text)

    changes = files.collect_planned_changes(
        tmp_path,
        sd.some_file("*.txt"),
        formatter=TEXT_FORMATTER,
    )

    assert sorted(changes, key=lambda x: x.file) == [
        PlannedChange(
            file=some_other_file,
            project_root=tmp_path,
            old_content=other_original_text,
            new_content=f"++{sd.SOME_OTHER_VERSION}++",
            newline=None,
        ),
        PlannedChange(
            file=some_file,
            project_root=tmp_path,
            old_content=original_text,
            new_content=f"--{sd.SOME_OTHER_VERSION}--\n",
            newline="\n",
        ),
    ]


def test_collect_planned_changes__multiline_search_replace__planned_change_with_expected_content(
    tmp_path: Path,
):
    original_text = f"abc\n--{sd.SOME_VERSION}--\nedf\n--{sd.SOME_VERSION}--\n"
    expected_text = f"abc\n--{sd.SOME_VERSION}--\nedf\n--{sd.SOME_OTHER_VERSION}--\n"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text(original_text)
    format_pattern = f"edf\n--{{{keys.VERSION}}}"

    changes = files.collect_planned_changes(
        tmp_path,
        sd.some_file(
            "*.txt",
            search_format_pattern=format_pattern,
            replace_format_pattern=format_pattern,
        ),
        formatter=TEXT_FORMATTER,
    )

    assert changes == [
        PlannedChange(
            file=some_file,
            project_root=tmp_path,
            old_content=original_text,
            new_content=expected_text,
            newline="\n",
        )
    ]


@pytest.mark.parametrize(
    ["text", "expected_line_ending"],
    [
        (f"--{sd.SOME_VERSION}--", None),
        (f"--{sd.SOME_VERSION}--\nabc", "\n"),
        (f"--{sd.SOME_VERSION}--\r\nabc", "\r\n"),
    ],
)
def test_collect_planned_changes__detect_line_ending__expected_ending(
    text: str, expected_line_ending: Optional[str], tmp_path: Path
):
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_bytes(text.encode())

    changes = files.collect_planned_changes(
        tmp_path,
        sd.some_file("*.txt"),
        formatter=TEXT_FORMATTER,
    )

    assert len(changes) == 1
    assert changes[0].newline == expected_line_ending


def test_collect_planned_changes__version_not_found__error(tmp_path: Path):
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text("")

    with pytest.raises(VersionNotFound):
        files.collect_planned_changes(
            tmp_path,
            sd.some_file(some_file.name),
            formatter=TEXT_FORMATTER,
        )


def test_collect_planned_changes__no_files_matched__error(tmp_path: Path):
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_text("")

    with pytest.raises(FileGlobError):
        files.collect_planned_changes(
            tmp_path,
            sd.some_file("non-existent.txt"),
            formatter=TEXT_FORMATTER,
        )


@pytest.mark.parametrize(
    ["newline", "expected_newline"],
    [
        (None, os.linesep),
        ("\n", "\n"),
        ("\r\n", "\r\n"),
    ],
)
def test_perform_change__file_updated_proper_end(
    newline: Optional[str], expected_newline: str, tmp_path: Path
):
    original_text = f"--{sd.SOME_VERSION}--\n"
    replacement_text = f"--{sd.SOME_OTHER_VERSION}--\n"
    some_file = tmp_path / SOME_FILE_NAME
    some_file.write_bytes(original_text.encode())

    files.perform_change(
        PlannedChange(
            file=some_file,
            project_root=tmp_path,
            old_content=original_text,
            new_content=replacement_text,
            newline=newline,
        )
    )

    expected = replacement_text.replace("\n", expected_newline).encode()
    assert some_file.read_bytes() == expected


def test_perform_change__invalid_file__error(tmp_path: Path):
    some_non_existent_file = tmp_path / "some_dir" / SOME_FILE_NAME

    with pytest.raises(ValueError):
        files.perform_change(
            PlannedChange(
                file=some_non_existent_file,
                project_root=tmp_path,
                old_content=f"--{sd.SOME_VERSION}--",
                new_content=f"--{sd.SOME_OTHER_VERSION}--",
                newline="\n",
            )
        )
