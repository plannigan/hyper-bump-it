from pathlib import Path

from semantic_version import Version

from hyper_bump_it._cli.interactive.top_level import InteractiveConfigEditor
from hyper_bump_it._config import ConfigFile


def config_update(
    initial_version: Version,
    initial_config: ConfigFile,
    pyproject: bool,
    project_root: Path,
) -> tuple[ConfigFile, bool]:
    return InteractiveConfigEditor(
        initial_version, initial_config, pyproject, project_root
    ).configure()
