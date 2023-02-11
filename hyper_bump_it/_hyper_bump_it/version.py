"""
Semantic version parsing and data structure.
"""
import re
from dataclasses import dataclass
from functools import cached_property, total_ordering
from typing import Union

from .compat import TypeAlias

# Implementation based on python-semanticverison, which is distributed under two-clause BSD license.

_IDENTIFIER_CHARS = "0-9A-Za-z-"
_IDENTIFIER_REGEX = f"[{_IDENTIFIER_CHARS}]+"
_VERSION_REGEX = (
    r"^(?P<major>\d+)\."
    r"(?P<minor>\d+)\."
    r"(?P<patch>\d+)"
    rf"(?:-(?P<prerelease>[{_IDENTIFIER_CHARS}.]+))?"
    rf"(?:\+(?P<build>[{_IDENTIFIER_CHARS}.]+))?$"
)


class _Max:
    def __eq__(self, other: object) -> bool:
        if isinstance(other, _Max):
            return True
        return NotImplemented


@dataclass
class _Numeric:
    value: int

    def __lt__(self, other: object) -> bool:
        if isinstance(other, _Numeric):
            return self.value < other.value
        if isinstance(other, (_Max, _Alpha)):
            return True
        return NotImplemented


@dataclass
class _Alpha:
    value: str

    def __lt__(self, other: object) -> bool:
        if isinstance(other, _Alpha):
            return self.value < other.value
        if isinstance(other, _Numeric):
            return False
        if isinstance(other, _Max):
            return True
        return NotImplemented


OrderingValue: TypeAlias = Union[int, _Max, _Numeric, _Alpha]


@total_ordering
@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_number(self.major, "major")
        _validate_number(self.minor, "minor")
        _validate_number(self.patch, "patch")
        _validate_tuple(self.prerelease, "prerelease", forbid_numeric_leading_zero=True)
        _validate_tuple(self.build, "build", forbid_numeric_leading_zero=False)

    def __str__(self) -> str:
        value = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            value = f"{value}-{'.'.join(self.prerelease)}"
        if self.build:
            value = f"{value}+{'.'.join(self.build)}"
        return value

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._ordering_key < other._ordering_key

    @cached_property
    def _ordering_key(self) -> tuple[OrderingValue, ...]:
        values: list[OrderingValue] = [self.major, self.minor, self.patch]
        if len(self.prerelease) == 0:
            values.append(_Max())
        else:
            for identifier in self.prerelease:
                values.append(
                    _Numeric(int(identifier))
                    if identifier.isdigit()
                    else _Alpha(identifier)
                )
        return tuple(values)

    def next_major(self) -> "Version":
        return Version(major=self.major + 1, minor=0, patch=0, prerelease=(), build=())

    def next_minor(self) -> "Version":
        return Version(
            major=self.major, minor=self.minor + 1, patch=0, prerelease=(), build=()
        )

    def next_patch(self) -> "Version":
        return Version(
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
            prerelease=(),
            build=(),
        )

    @classmethod
    def parse(cls, version_text: str) -> "Version":
        match = re.match(_VERSION_REGEX, version_text)
        if match is None:
            raise ValueError(f"Version text could not be parsed: {version_text}")

        return cls(
            major=_validate_number_group(match, "major"),
            minor=_validate_number_group(match, "minor"),
            patch=_validate_number_group(match, "patch"),
            prerelease=_group_to_tuple(match, "prerelease"),
            build=_group_to_tuple(match, "build"),
        )


def _validate_number(value: int, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must not be a negative number")


def _validate_tuple(
    identifiers: tuple[str, ...], name: str, forbid_numeric_leading_zero: bool
) -> None:
    for identifier in identifiers:
        if identifier == "":
            raise ValueError(f"{name} may not have an empty identifier")
        if re.match(f"^{_IDENTIFIER_REGEX}$", identifier) is None:
            raise ValueError(f"{name} contains an identifier with invalid characters")

        if (
            forbid_numeric_leading_zero
            and identifier.isdigit()
            and identifier[0] == "0"
        ):
            raise ValueError(f"{name} may not have a leading 0 for numeric identifier")


def _validate_number_group(match: re.Match[str], name: str) -> int:
    # Just validate the requirements of string to int operation.
    # _validate_number() is used for int specific validation.
    value = match.group(name)
    if value != "0" and value.startswith("0"):
        raise ValueError(f"{name} may not have a leading zero")
    return int(value)


def _group_to_tuple(match: re.Match[str], name: str) -> tuple[str, ...]:
    value = match.group(name)
    if value is None:
        return ()
    return tuple(value.split("."))
