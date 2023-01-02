"""
Go through a series of prompts to construct a custom files configuration.
"""
from hyper_bump_it._config import FileDefinition


class FilesConfigEditor:
    def __init__(self, initial_config: list[FileDefinition]) -> None:
        self._config = [file.copy() for file in initial_config]

    def configure(self) -> list[FileDefinition]:
        return self._config
