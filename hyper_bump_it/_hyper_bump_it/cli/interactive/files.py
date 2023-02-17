"""
Go through a series of prompts to construct a custom files configuration.
"""
from enum import Enum
from typing import Optional

from rich.text import Text

from ... import ui
from ...config import DEFAULT_SEARCH_PATTERN, FileDefinition
from ..common import EXAMPLE_FILE_GLOB
from .file_validation import DefinitionValidator

_EXAMPLE_DEFINITION = FileDefinition(file_glob=EXAMPLE_FILE_GLOB)


class FilesMenu(Enum):
    Add = "add"
    Remove = "remove"
    Edit = "edit"
    List = "list"
    Done = "done"


class FilesConfigEditor:
    def __init__(
        self, initial_config: list[FileDefinition], validator: DefinitionValidator
    ) -> None:
        self._config = [file.copy() for file in initial_config]
        self._validator = validator
        self._config_funcs = {
            FilesMenu.Add: self._add_definition,
            FilesMenu.Remove: self._remove_definition,
            FilesMenu.Edit: self._edit_definition,
            FilesMenu.List: self._list_definitions,
        }

    def configure(self) -> tuple[list[FileDefinition], bool]:
        if self._config == [_EXAMPLE_DEFINITION]:
            if _prompt_replace_example():
                ui.blank_line()
                self._config = []
                self._add_definition()
            else:
                ui.blank_line()
        while (selection := _prompt_file_menu()) is not FilesMenu.Done:
            ui.blank_line()
            self._config_funcs[selection]()

        ui.blank_line()
        return self._config, self._has_keystone

    @property
    def _has_keystone(self) -> bool:
        return any(definition.keystone for definition in self._config)

    def _add_definition(self) -> None:
        self._config.append(
            _prompt_definition(None, self._has_keystone, self._validator)
        )

    def _remove_definition(self) -> None:
        if len(self._config) == 1:
            index = 0
        else:
            index, _ = _prompt_select_definition("remove", self._config)
            ui.blank_line()
        del self._config[index]
        if len(self._config) == 0:
            ui.display(
                "There must be at least one file definition. A new definition must be added now."
            )
            self._add_definition()

    def _edit_definition(self) -> None:
        if len(self._config) == 1:
            index = 0
            definition = self._config[0]
        else:
            index, definition = _prompt_select_definition("edit", self._config)
            ui.blank_line()
        self._config[index] = _prompt_definition(
            definition, self._has_keystone, self._validator
        )

    def _list_definitions(self) -> None:
        ui.display("The current file definitions:")
        for definition in self._config:
            ui.display(_definition_summary(definition))
        ui.blank_line()


def _prompt_file_menu() -> FilesMenu:
    return ui.choice_enum(
        "What file operation would you like to perform?",
        option_descriptions={
            FilesMenu.Add: "Add a new file definition",
            FilesMenu.Remove: "Remove a file definition",
            FilesMenu.Edit: "Edit an existing file definition",
            FilesMenu.List: "Display all of the file definitions",
            FilesMenu.Done: "Stop editing the file definitions",
        },
        default=FilesMenu.Done,
    )


def _prompt_file_glob(default: Optional[str]) -> str:
    if default is None:
        return ui.ask("Enter the glob pattern to match one or more files")

    message = Text("The current file glob pattern is '")
    message.append(default, style="file.glob")
    message.append(
        "'.\nEnter a new glob pattern or leave it blank to keep the current file glob pattern"
    )
    return ui.ask(message, default=default)


def _prompt_definition(
    current: Optional[FileDefinition],
    has_keystone: bool,
    validator: DefinitionValidator,
) -> FileDefinition:
    ui.display("Enter details for the file definition.")
    while True:
        file_glob = _prompt_file_glob(
            default=None if current is None else current.file_glob
        )
        ui.blank_line()
        if current is None:
            new = True
            current_search_pattern = DEFAULT_SEARCH_PATTERN
            current_replace_pattern = None
        else:
            new = False
            current_search_pattern = current.search_format_pattern
            current_replace_pattern = current.replace_format_pattern

        search_format_pattern = _prompt_format_pattern(
            "search", current_search_pattern, new=new
        )
        ui.blank_line()
        replace_format_pattern = _prompt_replace_format_pattern(
            current_replace_pattern, current_search_pattern, new
        )
        ui.blank_line()
        keystone = _keystone_selection(
            has_keystone, False if current is None else current.keystone
        )
        definition = FileDefinition(
            file_glob=file_glob,
            keystone=keystone,
            search_format_pattern=search_format_pattern,
            replace_format_pattern=replace_format_pattern,
        )
        ui.blank_line()
        result = validator(definition)
        if result is None:
            return definition

        ui.display("The configured file definition was not valid:")
        ui.display(result.description)
        ui.display("Update the definition to address the issue.")
        ui.blank_line()
        # Replace current with the new definition so the prompt defaults match what the user
        # entered. This allows the user to quickly get to the prompt that needs to be addressed.
        current = definition


def _keystone_selection(has_keystone: bool, current_keystone: Optional[bool]) -> bool:
    if has_keystone:
        if current_keystone:
            return _prompt_keystone(default=True)
        ui.display(
            "A file definition is already the keystone. Edit that definition in order to"
            " make this the keystone file"
        )
        return False
    ui.display(
        "A keystone file can be used instead of explicitly storing the current version in "
        "the configuration file."
    )
    return _prompt_keystone(default=False)


def _prompt_keystone(default: bool) -> bool:
    return ui.confirm(
        "Do you want this file definition to be a keystone file?",
        default=default,
    )


def _prompt_format_pattern(name: str, current: str, new: bool) -> str:
    description = "default" if new else "current"
    message = Text("The ")
    message.append(description)
    message.append(" ")
    message.append(name)
    message.append(" format pattern is '")
    message.append(_newline_display(current), style="format.pattern")
    message.append("'.\nEnter a new format pattern or leave it blank to keep the ")
    message.append(description)
    message.append(" format pattern")
    return ui.ask(
        message,
        default=current,
    ).replace("\\n", "\n")


def _prompt_replace_format_pattern(
    current: Optional[str], search_pattern: str, new: bool
) -> Optional[str]:
    use_search_pattern = ui.confirm(
        "The replace format pattern can be omitted. In this case, the search format pattern value "
        "is used.\n"
        "Do you want omit the replace format pattern?",
        default=new or current is None,
    )
    ui.blank_line()
    if use_search_pattern:
        return None
    return _prompt_format_pattern(
        "replace", search_pattern if current is None else current, new
    )


def _prompt_select_definition(
    action: str, definitions: list[FileDefinition]
) -> tuple[int, FileDefinition]:
    prompt_text = Text()
    options = {
        str(i): _definition_summary(definition)
        for i, definition in enumerate(definitions)
    }
    prompt_text.append_text(ui.list_options(options))
    prompt_text.append(f"Enter the number for the file definition to {action}")
    selected_index = ui.choice_int(
        prompt_text,
        choices=list(options.keys()),
    )
    return selected_index, definitions[selected_index]


def _prompt_replace_example() -> bool:
    return ui.confirm(
        "The configuration currently only has an example definition. Do you want to replace it?",
        default=True,
    )


def _definition_summary(definition: FileDefinition) -> Text:
    if definition.replace_format_pattern is None:
        replace_format_pattern = definition.search_format_pattern
    else:
        replace_format_pattern = definition.replace_format_pattern
    summary = Text("file-glob: '")
    summary.append(definition.file_glob, style="file.glob")
    summary.append("' search-format-pattern: '")
    summary.append(
        _newline_display(definition.search_format_pattern), style="format.pattern"
    )
    summary.append("' replace-format-pattern: '")
    summary.append(_newline_display(replace_format_pattern), style="format.pattern")
    summary.append("'")
    if definition.keystone:
        summary.append(" (keystone)")
    return summary


def _newline_display(pattern: str) -> str:
    return pattern.replace("\n", "\\n")
