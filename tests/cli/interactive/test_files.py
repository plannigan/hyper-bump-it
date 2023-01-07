from io import StringIO

import pytest

from hyper_bump_it._cli.interactive import files
from hyper_bump_it._cli.interactive.files import FilesMenu
from hyper_bump_it._config import FileDefinition
from tests import sample_data as sd
from tests.conftest import ForceInput

EXAMPLE_CONFIG = [files._EXAMPLE_DEFINITION]


def test_configure__no_changes__same_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    initial_config = [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            replace_format_pattern=sd.SOME_REPLACE_FORMAT_PATTERN,
        )
    ]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__example_definition_accept__unchanged_config(
    force_input: ForceInput,
):
    force_input("n", force_input.NO_INPUT)
    editor = files.FilesConfigEditor(EXAMPLE_CONFIG)

    result = editor.configure()

    assert result == EXAMPLE_CONFIG


def test_configure__example_definition_change__prompt_replacement_definition(
    force_input: ForceInput,
):
    force_input(
        "y",  # yes, replace example
        sd.SOME_FILE_GLOB,
        sd.SOME_SEARCH_FORMAT_PATTERN,
        "y",  # yes, omit replace format pattern
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    editor = files.FilesConfigEditor(EXAMPLE_CONFIG)

    result = editor.configure()

    assert result == [
        FileDefinition(
            file_glob=sd.SOME_FILE_GLOB,
            keystone=False,
            search_format_pattern=sd.SOME_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=None,
        )
    ]


def test_configure__no_edit__unchanged_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    initial_config = [sd.some_file_definition()]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__add__addition_definition(force_input: ForceInput):
    force_input(
        FilesMenu.Add.value,
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition()]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config + [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]


def test_configure__add_keystone_exists__new_definition_cant_be_keystone(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        FilesMenu.Add.value,
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        # no option to select keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition(keystone=True)]
    editor = files.FilesConfigEditor(initial_config)

    editor.configure()

    assert "A file definition is already the keystone." in capture_rich.getvalue()


def test_configure__remove_from_single__remove_require_addition(
    force_input: ForceInput,
):
    force_input(
        FilesMenu.Remove.value,
        # no index selection needed
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition()]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]


def test_configure__remove_from_multiple__remove_definition(force_input: ForceInput):
    force_input(
        FilesMenu.Remove.value,
        "0",  # index selection
        force_input.NO_INPUT,
    )
    some_definition = sd.some_file_definition()
    some_other_definition = sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)
    editor = files.FilesConfigEditor([some_definition, some_other_definition])

    result = editor.configure()

    assert result == [some_other_definition]


def test_configure__edit_from_single__edited_definition(
    force_input: ForceInput,
):
    force_input(
        FilesMenu.Edit.value,
        # no index selection needed
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition()]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]


def test_configure__edit_default__unchanged_config(
    force_input: ForceInput,
):
    force_input(
        FilesMenu.Edit.value,
        # no index selection needed
        force_input.NO_INPUT,  # file glob
        force_input.NO_INPUT,  # search pattern
        force_input.NO_INPUT,  # omit replace pattern
        force_input.NO_INPUT,  # replace pattern
        force_input.NO_INPUT,  # keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition()]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == initial_config


def test_configure__edit_from_single_keystone__edited_definition(
    force_input: ForceInput,
):
    force_input(
        FilesMenu.Edit.value,
        # no index selection needed
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition(keystone=True)]
    editor = files.FilesConfigEditor(initial_config)

    result = editor.configure()

    assert result == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            keystone=False,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]


def test_configure__edit_from_multiple__edited_selected_definition(
    force_input: ForceInput,
):
    force_input(
        FilesMenu.Edit.value,
        "0",  # index selection
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    some_definition = sd.some_file_definition()
    some_other_definition = sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)
    editor = files.FilesConfigEditor([some_definition, some_other_definition])

    result = editor.configure()

    assert result == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        ),
        some_other_definition,
    ]


def test_configure__list__display_definitions(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        FilesMenu.List.value,
        force_input.NO_INPUT,
    )
    some_definition = sd.some_file_definition()
    some_other_definition = sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)
    editor = files.FilesConfigEditor([some_definition, some_other_definition])

    editor.configure()
    assert (
        f"{files._definition_summary(some_definition)}\n{files._definition_summary(some_other_definition)}"
        in capture_rich.getvalue()
    )


@pytest.mark.parametrize(
    [
        "file_glob",
        "keystone",
        "search_format_pattern",
        "replace_format_pattern",
        "expected_output",
    ],
    [
        (
            sd.SOME_FILE_GLOB,
            False,
            sd.SOME_SEARCH_FORMAT_PATTERN,
            None,
            f"file-glob: '{sd.SOME_FILE_GLOB}' "
            f"search-format-pattern: '{sd.SOME_SEARCH_FORMAT_PATTERN}' "
            f"replace-format-pattern: '{sd.SOME_SEARCH_FORMAT_PATTERN}'",
        ),
        (
            sd.SOME_FILE_GLOB,
            False,
            sd.SOME_SEARCH_FORMAT_PATTERN,
            sd.SOME_REPLACE_FORMAT_PATTERN,
            f"file-glob: '{sd.SOME_FILE_GLOB}' "
            f"search-format-pattern: '{sd.SOME_SEARCH_FORMAT_PATTERN}' "
            f"replace-format-pattern: '{sd.SOME_REPLACE_FORMAT_PATTERN}'",
        ),
        (
            sd.SOME_FILE_GLOB,
            True,
            sd.SOME_SEARCH_FORMAT_PATTERN,
            None,
            f"file-glob: '{sd.SOME_FILE_GLOB}' "
            f"search-format-pattern: '{sd.SOME_SEARCH_FORMAT_PATTERN}' "
            f"replace-format-pattern: '{sd.SOME_SEARCH_FORMAT_PATTERN}' "
            f"(keystone)",
        ),
        (
            sd.SOME_FILE_GLOB,
            True,
            sd.SOME_SEARCH_FORMAT_PATTERN,
            sd.SOME_REPLACE_FORMAT_PATTERN,
            f"file-glob: '{sd.SOME_FILE_GLOB}' "
            f"search-format-pattern: '{sd.SOME_SEARCH_FORMAT_PATTERN}' "
            f"replace-format-pattern: '{sd.SOME_REPLACE_FORMAT_PATTERN}' "
            f"(keystone)",
        ),
    ],
)
def test_file_summary__default_search_pattern__formats_to_version(
    file_glob, keystone, search_format_pattern, replace_format_pattern, expected_output
):
    some_file = FileDefinition(
        file_glob=file_glob,
        keystone=keystone,
        search_format_pattern=search_format_pattern,
        replace_format_pattern=replace_format_pattern,
    )

    assert files._definition_summary(some_file) == expected_output
