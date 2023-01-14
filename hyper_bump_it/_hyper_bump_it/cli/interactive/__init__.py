from pathlib import Path

from ...config import ConfigFile
from .top_level import InteractiveConfigEditor


def config_update(
    initial_config: ConfigFile,
    pyproject: bool,
    project_root: Path,
) -> tuple[ConfigFile, bool]:
    return InteractiveConfigEditor(initial_config, pyproject, project_root).configure()
