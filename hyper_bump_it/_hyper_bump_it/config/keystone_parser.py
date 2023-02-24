"""
Use format patterns to produce regular expression matching patterns to determine the current
version from a keystone file.
"""
from pathlib import Path
from re import Match
from typing import Optional

from ..error import IncompleteKeystoneVersionError, VersionNotFound
from ..format_pattern import create_matching_pattern, keys
from ..version import Version


def find_current_version(
    file: Path,
    search_pattern: str,
) -> Version:
    """
    Search a file for the version based on a given search pattern.

    :param file: File to read contents from.
    :param search_pattern: Format pattern to use for identifying the version.
    :return: Parsed version found in the file.
    :raises FormatError: There was an issue processing the keystone version using the search
        pattern.
    :raises VersionNotFound: None of the lines in the file matched the search pattern.
    """
    matching_pattern = create_matching_pattern(search_pattern)
    if (match := matching_pattern.search(file.read_text())) is not None:
        version_string = _version_string_from_match(match)
        if version_string is None:
            raise IncompleteKeystoneVersionError(file, search_pattern)
        return Version.parse(version_string)

    raise VersionNotFound(file, search_pattern)


def _version_string_from_match(match: Match[str]) -> Optional[str]:
    # Work through the matched groups to rebuild the version data.
    # Prefer general keys to explicit current keys.
    # Ignore explicit new and extra keys
    groups = match.groupdict()
    # fast path for full version keys
    for version_key in (keys.VERSION, keys.CURRENT_VERSION):
        if (version_string := groups.get(version_key)) is not None:
            return version_string

    version_group_keys = {
        "major": (keys.MAJOR, keys.CURRENT_MAJOR),
        "minor": (keys.MINOR, keys.CURRENT_MINOR),
        "patch": (keys.PATCH, keys.CURRENT_PATCH),
        "prerelease": (keys.PRERELEASE, keys.CURRENT_PRERELEASE),
        "build": (keys.BUILD, keys.CURRENT_BUILD),
    }

    values: dict[str, str] = {}
    for version_part, part_keys in version_group_keys.items():
        for part_key in part_keys:
            if (part_value := groups.get(part_key)) is not None:
                values[version_part] = part_value
                break

    return _build_version(values)


def _build_version(values: dict[str, str]) -> Optional[str]:
    try:
        version_string = "{major}.{minor}.{patch}".format(
            major=values["major"],
            minor=values["minor"],
            patch=values["patch"],
        )
    except KeyError:
        return None

    if "prerelease" in values:
        version_string = f'{version_string}-{values["prerelease"]}'
    if "build" in values:
        version_string = f'{version_string}+{values["build"]}'
    return version_string
