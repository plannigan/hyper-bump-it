from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from ..version import Version
from .core import GitAction


class BumpPart(str, Enum):
    Major = "major"
    Minor = "minor"
    Patch = "patch"


@dataclass
class BumpToArgs:
    new_version: Version
    config_file: Optional[Path]  # absolute resolved path
    project_root: Path  # absolute resolved path
    dry_run: bool
    patch: bool
    skip_confirm_prompt: Optional[bool]
    current_version: Optional[Version]
    commit: Optional[GitAction]
    branch: Optional[GitAction]
    tag: Optional[GitAction]
    remote: Optional[str]
    commit_format_pattern: Optional[str]
    branch_format_pattern: Optional[str]
    tag_format_pattern: Optional[str]
    allowed_initial_branches: Optional[frozenset[str]]


@dataclass
class BumpByArgs:
    part_to_bump: BumpPart
    config_file: Optional[Path]  # absolute resolved path
    project_root: Path  # absolute resolved path
    dry_run: bool
    patch: bool
    skip_confirm_prompt: Optional[bool]
    current_version: Optional[Version]
    commit: Optional[GitAction]
    branch: Optional[GitAction]
    tag: Optional[GitAction]
    remote: Optional[str]
    commit_format_pattern: Optional[str]
    branch_format_pattern: Optional[str]
    tag_format_pattern: Optional[str]
    allowed_initial_branches: Optional[frozenset[str]]
