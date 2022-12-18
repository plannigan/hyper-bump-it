from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from semantic_version import Version

from hyper_bump_it._config.core import GitAction


class BumpPart(str, Enum):
    Major = "major"
    Minor = "minor"
    Patch = "patch"


@dataclass
class BumpToArgs:
    new_version: Version
    config_file: Optional[Path]
    project_root: Path
    dry_run: bool
    skip_confirm_prompt: Optional[bool]
    current_version: Optional[Version]
    commit: Optional[GitAction]
    branch: Optional[GitAction]
    tag: Optional[GitAction]
    remote: Optional[str]
    commit_format_pattern: Optional[str]
    branch_format_pattern: Optional[str]
    tag_format_pattern: Optional[str]


@dataclass
class BumpByArgs:
    part_to_bump: BumpPart
    config_file: Optional[Path]
    project_root: Path
    dry_run: bool
    skip_confirm_prompt: Optional[bool]
    current_version: Optional[Version]
    commit: Optional[GitAction]
    branch: Optional[GitAction]
    tag: Optional[GitAction]
    remote: Optional[str]
    commit_format_pattern: Optional[str]
    branch_format_pattern: Optional[str]
    tag_format_pattern: Optional[str]
