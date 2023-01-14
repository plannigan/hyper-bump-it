from io import StringIO
from typing import Optional, cast

import pytest

from hyper_bump_it._hyper_bump_it.cli.interactive import files
from hyper_bump_it._hyper_bump_it.cli.interactive.file_validation import (
    DefinitionValidator,
    FailureType,
    ValidationFailure,
)
from hyper_bump_it._hyper_bump_it.cli.interactive.files import FilesMenu
from hyper_bump_it._hyper_bump_it.config import FileDefinition
from tests._hyper_bump_it import sample_data as sd
from tests.conftest import ForceInput

EXAMPLE_CONFIG = [files._EXAMPLE_DEFINITION]
ALWAYS_VALID = cast(DefinitionValidator, lambda _: None)


def create_invalid_first() -> DefinitionValidator:
    was_called = False

    def _validator(_) -> Optional[ValidationFailure]:
        nonlocal was_called
        if was_called:
            return None
        was_called = True
        return ValidationFailure(FailureType.NoFiles, "")

    return cast(DefinitionValidator, _validator)


def test_configure__no_changes__same_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    initial_config = [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            replace_format_pattern=sd.SOME_REPLACE_FORMAT_PATTERN,
        )
    ]
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == initial_config
    assert result_has_keystone is False


def test_configure__example_definition_accept__unchanged_config(
    force_input: ForceInput,
):
    force_input("n", force_input.NO_INPUT)
    editor = files.FilesConfigEditor(EXAMPLE_CONFIG, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == EXAMPLE_CONFIG
    assert result_has_keystone is False


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
    editor = files.FilesConfigEditor(EXAMPLE_CONFIG, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == [
        FileDefinition(
            file_glob=sd.SOME_FILE_GLOB,
            keystone=False,
            search_format_pattern=sd.SOME_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=None,
        )
    ]
    assert result_has_keystone is False


def test_configure__no_edit__unchanged_config(force_input: ForceInput):
    force_input(force_input.NO_INPUT)
    initial_config = [sd.some_file_definition()]
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == initial_config
    assert result_has_keystone is False


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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == initial_config + [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]
    assert result_has_keystone is False


def test_configure__add_keystone_exists__result_has_keystone(
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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == initial_config + [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            keystone=False,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]
    assert result_has_keystone is True


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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    editor.configure()

    assert "A file definition is already the keystone." in capture_rich.getvalue()


def test_configure__add_invalid__prompted_again(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        FilesMenu.Add.value,
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_INVALID_FORMAT_PATTERN,
        "y",  # yes, omit replace format pattern
        "n",  # no, keystone
        # start again
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_SEARCH_FORMAT_PATTERN,
        "y",  # yes, omit replace format pattern
        "n",  # no, keystone
        force_input.NO_INPUT,
    )
    editor = files.FilesConfigEditor(
        [sd.some_file_definition()], create_invalid_first()
    )

    editor.configure()

    assert "The configured file definition was not valid:" in capture_rich.getvalue()


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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]
    assert result_has_keystone is False


def test_configure__remove_from_multiple__remove_definition(force_input: ForceInput):
    force_input(
        FilesMenu.Remove.value,
        "0",  # index selection
        force_input.NO_INPUT,
    )
    some_definition = sd.some_file_definition()
    some_other_definition = sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)
    editor = files.FilesConfigEditor(
        [some_definition, some_other_definition], ALWAYS_VALID
    )

    result_config, result_has_keystone = editor.configure()

    assert result_config == [some_other_definition]
    assert result_has_keystone is False


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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]
    assert result_has_keystone is False


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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == initial_config
    assert result_has_keystone is False


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
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            keystone=False,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]
    assert result_has_keystone is False


def test_configure__edit_to_single_keystone__edited_definition(
    force_input: ForceInput,
):
    force_input(
        FilesMenu.Edit.value,
        # no index selection needed
        sd.SOME_OTHER_FILE_GLOB,
        sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
        "n",  # no, explicit replace format pattern
        sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        "y",  # yes, keystone
        force_input.NO_INPUT,
    )
    initial_config = [sd.some_file_definition(keystone=False)]
    editor = files.FilesConfigEditor(initial_config, ALWAYS_VALID)

    result_config, result_has_keystone = editor.configure()

    assert result_config == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            keystone=True,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        )
    ]
    assert result_has_keystone is True


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
    editor = files.FilesConfigEditor(
        [some_definition, some_other_definition], ALWAYS_VALID
    )

    result_config, result_has_keystone = editor.configure()

    assert result_config == [
        sd.some_file_definition(
            file_glob=sd.SOME_OTHER_FILE_GLOB,
            search_format_pattern=sd.SOME_OTHER_SEARCH_FORMAT_PATTERN,
            replace_format_pattern=sd.SOME_OTHER_REPLACE_FORMAT_PATTERN,
        ),
        some_other_definition,
    ]
    assert result_has_keystone is False


def test_configure__list__display_definitions(
    force_input: ForceInput, capture_rich: StringIO
):
    force_input(
        FilesMenu.List.value,
        force_input.NO_INPUT,
    )
    some_definition = sd.some_file_definition()
    some_other_definition = sd.some_file_definition(file_glob=sd.SOME_OTHER_FILE_GLOB)
    editor = files.FilesConfigEditor(
        [some_definition, some_other_definition], ALWAYS_VALID
    )

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
