"""
Go through a series of prompts to construct a custom files configuration.
"""
from enum import Enum
from typing import Optional

from rich import print, prompt
from rich.text import Text

from hyper_bump_it._cli.common import EXAMPLE_FILE_GLOB
from hyper_bump_it._cli.interactive.file_validation import DefinitionValidator
from hyper_bump_it._cli.interactive.prompt import enum_prompt, list_options
from hyper_bump_it._config import DEFAULT_SEARCH_PATTERN, FileDefinition

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
                self._config = []
                self._add_definition()
        while (selection := _prompt_file_menu()) is not FilesMenu.Done:
            self._config_funcs[selection]()

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
        del self._config[index]
        if len(self._config) == 0:
            print(
                "There must be at least one file definition. A new definition must be added now."
            )
            self._add_definition()

    def _edit_definition(self) -> None:
        if len(self._config) == 1:
            index = 0
            definition = self._config[0]
        else:
            index, definition = _prompt_select_definition("edit", self._config)
        self._config[index] = _prompt_definition(
            definition, self._has_keystone, self._validator
        )

    def _list_definitions(self) -> None:
        print("The current file definitions:")
        for definition in self._config:
            print(_definition_summary(definition))


def _prompt_file_menu() -> FilesMenu:
    return enum_prompt(
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
        file_glob = prompt.Prompt.ask(
            "Enter the glob pattern to match one or more files"
        )
    else:
        file_glob = prompt.Prompt.ask(
            f"The current file glob pattern is '{default}'\n."
            f"Enter a new glob pattern or leave it blank to kep the current file glob pattern",
            show_default=False,
            default=default,
        )

    return file_glob


def _prompt_definition(
    current: Optional[FileDefinition],
    has_keystone: bool,
    validator: DefinitionValidator,
) -> FileDefinition:
    print("Enter details for the file definition.")
    while True:
        file_glob = _prompt_file_glob(
            default=None if current is None else current.file_glob
        )
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
        replace_format_pattern = _prompt_replace_format_pattern(
            current_replace_pattern, current_search_pattern, new
        )
        keystone = _keystone_selection(
            has_keystone, False if current is None else current.keystone
        )
        definition = FileDefinition(
            file_glob=file_glob,
            keystone=keystone,
            search_format_pattern=search_format_pattern,
            replace_format_pattern=replace_format_pattern,
        )
        result = validator(definition)
        if result is None:
            return definition

        print("The configured file definition was not valid:")
        print(result.description)
        print("Update the definition to address the issue.")
        # Replace current with the new definition so the prompt defaults match what the user
        # entered. This allows the user to quickly get to the prompt that needs to be addressed.
        current = definition


def _keystone_selection(has_keystone: bool, current_keystone: Optional[bool]) -> bool:
    if has_keystone:
        if current_keystone:
            return _prompt_keystone(default=True)
        print(
            "A file definition is already the keystone. Edit that definition in order to"
            " make this the keystone file"
        )
        return False
    print(
        "A keystone file can be used instead of explicitly storing the current version in "
        "the configuration file."
    )
    return _prompt_keystone(default=False)


def _prompt_keystone(default: bool) -> bool:
    return prompt.Confirm.ask(
        "Do you want this file definition to be a keystone file?",
        default=default,
    )


def _prompt_format_pattern(name: str, current: str, new: bool) -> str:
    description = "default" if new else "current"
    return prompt.Prompt.ask(
        f"The {description} {name} format pattern is '{current}'.\n"
        f"Enter a new format pattern or leave it blank to kep the {description} format pattern",
        show_default=False,
        default=current,
    )


def _prompt_replace_format_pattern(
    current: Optional[str], search_pattern: str, new: bool
) -> Optional[str]:
    use_search_pattern = prompt.Confirm.ask(
        "The replace format pattern can be omitted. In this case, the search format pattern value "
        "is used.\n"
        "Do you want omit the replace format pattern?",
        default=new or current is None,
    )
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
    list_options(prompt_text, options)
    prompt_text.append(f"Enter the number for the file definition to {action}")
    selected_index = prompt.IntPrompt.ask(
        prompt_text,
        choices=list(options.keys()),
        show_choices=False,
        show_default=False,
    )
    return selected_index, definitions[selected_index]


def _prompt_replace_example() -> bool:
    return prompt.Confirm.ask(
        "The configuration currently only has an example definition. Do you want to replace it?",
        default=True,
    )


def _definition_summary(definition: FileDefinition) -> str:
    if definition.replace_format_pattern is None:
        replace_format_pattern = definition.search_format_pattern
    else:
        replace_format_pattern = definition.replace_format_pattern
    return (
        f"file-glob: '{definition.file_glob}' "
        f"search-format-pattern: '{definition.search_format_pattern}' "
        f"replace-format-pattern: '{replace_format_pattern}'"
        f"{' (keystone)' if definition.keystone else ''}"
    )
