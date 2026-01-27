from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ..version import Version
from .core import GitAction


class BumpPart(str, Enum):
    Major = "major"
    Minor = "minor"
    Patch = "patch"


@dataclass
class BumpToArgs:
    new_version: Version
    config_file: Path | None  # absolute resolved path
    project_root: Path  # absolute resolved path
    dry_run: bool
    patch: bool
    skip_confirm_prompt: bool | None
    current_version: Version | None
    commit: GitAction | None
    branch: GitAction | None
    tag: GitAction | None
    remote: str | None
    commit_format_pattern: str | None
    branch_format_pattern: str | None
    tag_name_format_pattern: str | None
    tag_message_format_pattern: str | None
    allowed_initial_branches: frozenset[str] | None


@dataclass
class BumpByArgs:
    part_to_bump: BumpPart
    config_file: Path | None  # absolute resolved path
    project_root: Path  # absolute resolved path
    dry_run: bool
    patch: bool
    skip_confirm_prompt: bool | None
    current_version: Version | None
    commit: GitAction | None
    branch: GitAction | None
    tag: GitAction | None
    remote: str | None
    commit_format_pattern: str | None
    branch_format_pattern: str | None
    tag_name_format_pattern: str | None
    tag_message_format_pattern: str | None
    allowed_initial_branches: frozenset[str] | None
