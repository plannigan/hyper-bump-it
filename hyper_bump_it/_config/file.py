from enum import Enum
from typing import Optional, Union, cast

from pydantic import BaseModel, Field, StrictBool, StrictStr, root_validator

from hyper_bump_it._text_formatter import keys


class GitFileAction(str, Enum):
    Skip = "skip"
    Create = "create"
    CreateAndPush = "create-and-push"


class HyperBaseMode(BaseModel):
    class Config:
        extra = "forbid"
        min_anystr_length = 1
        allow_mutation = False


class GitActions(HyperBaseMode):
    commit: GitFileAction = GitFileAction.Create
    branch: GitFileAction = GitFileAction.Skip
    tag: GitFileAction = GitFileAction.Skip


class Git(HyperBaseMode):
    remote: StrictStr = "origin"
    commit_format_pattern: StrictStr = (
        f"Bump version: {{{keys.CURRENT_VERSION}}} → {{{keys.NEW_VERSION}}}"
    )
    branch_format_pattern: StrictStr = f"bump_version_to_{{{keys.NEW_VERSION}}}"
    tag_format_pattern: StrictStr = f"v{{{keys.NEW_VERSION}}}"
    actions: GitActions = GitActions()


class File(HyperBaseMode):
    file_glob: StrictStr  # relative to project root directory
    keystone: StrictBool = False
    search_format_pattern: StrictStr = keys.VERSION
    replace_format_pattern: Optional[StrictStr] = None


HyperConfigFileValues = dict[str, Union[list[File], Optional[StrictStr], Git]]


class ConfigFile(HyperBaseMode):
    files: list[File] = Field(..., min_items=1)
    current_version: Optional[StrictStr] = None
    git: Git = Git()

    @root_validator(skip_on_failure=True)
    def check_keystone_files(
        cls,
        values: HyperConfigFileValues,
    ) -> HyperConfigFileValues:
        files = cast(list[File], values["files"])
        keystone_file_count = sum(1 for file in files if file.keystone)
        if keystone_file_count > 1:
            raise ValueError("Only one file is allowed to be a keystone file")
        current_version = values.get("current_version")
        if current_version is None:
            if keystone_file_count == 0:
                raise ValueError(
                    "current_version must be set if there is not a keystone file"
                )
        elif keystone_file_count != 0:
            raise ValueError(
                "Configuration can't specify the current_version while also having a keystone file"
            )
        return values
