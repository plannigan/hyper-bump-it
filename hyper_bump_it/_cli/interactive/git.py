"""
Go through a series of prompts to construct a custom Git integration configuration.
"""
from hyper_bump_it._config import GitConfigFile


class GitConfigEditor:
    def __init__(self, initial_config: GitConfigFile) -> None:
        self._config = initial_config.copy(deep=True)

    def configure(self) -> GitConfigFile:
        return self._config
