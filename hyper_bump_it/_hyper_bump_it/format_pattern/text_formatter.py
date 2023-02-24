"""
Central place for performing text formatting.
"""
from datetime import date
from enum import Enum, auto
from string import Formatter
from typing import Optional

from ..error import FormatKeyError, FormatPatternError
from ..version import Version
from . import keys


class FormatContext(Enum):
    search = auto()
    replace = auto()


class TextFormatter:
    def __init__(
        self,
        current_version: Version,
        new_version: Version,
        today: Optional[date] = None,
    ) -> None:
        """
        Initialize an instance.

        :param current_version: Software version that is currently in use.
        :param new_version: Updated software version that is intended to be used as a replacement.
        :param today: The current date. If not provided `date.today()` will be used.
        """
        self._current_version = current_version
        self._new_version = new_version
        self._today = today or date.today()

    def format(
        self, format_pattern: str, context: Optional[FormatContext] = None
    ) -> str:
        """
        Perform string formatting on the given pattern.

        NOTE: If `context` is `FormatContext.search`, the "today" key will NOT be altered.
        This allows for converting just that key into a regex expression later.

        :param format_pattern: Pattern to be formatted.
        :param context: What context the format pattern is being evaluated. This controls that
            values used for the optional general keys. Default: None.
        :return: Result of string formatting.
        :raises FormatError: Format pattern was invalid or attempted to use an invalid key.
        """
        # NOTE: pre-release and build may not exist for a version. If that is the case and the
        # pattern uses those keys, the resultant value will be an empty string.
        values = {
            keys.CURRENT_VERSION: self._current_version,
            keys.CURRENT_MAJOR: self._current_version.major,
            keys.CURRENT_MINOR: self._current_version.minor,
            keys.CURRENT_PATCH: self._current_version.patch,
            keys.CURRENT_PRERELEASE: _merge_parts(self._current_version.prerelease),
            keys.CURRENT_BUILD: _merge_parts(self._current_version.build),
            keys.NEW_VERSION: self._new_version,
            keys.NEW_MAJOR: self._new_version.major,
            keys.NEW_MINOR: self._new_version.minor,
            keys.NEW_PATCH: self._new_version.patch,
            keys.NEW_PRERELEASE: _merge_parts(self._new_version.prerelease),
            keys.NEW_BUILD: _merge_parts(self._new_version.build),
            keys.TODAY: self._today,
        }

        def _add_general(version: Version) -> None:
            values[keys.VERSION] = version
            values[keys.MAJOR] = version.major
            values[keys.MINOR] = version.minor
            values[keys.PATCH] = version.patch
            values[keys.PRERELEASE] = _merge_parts(version.prerelease)
            values[keys.BUILD] = _merge_parts(version.build)

        if context is not None:
            if context == FormatContext.search:
                _add_general(self._current_version)
                # override to preserve format pattern so a second pass can convert it into a regex
                values[keys.TODAY] = PreserveFormat(keys.TODAY)
            else:
                _add_general(self._new_version)

        try:
            return format_pattern.format(**values)
        except (KeyError, IndexError):
            raise FormatKeyError(format_pattern, values.keys())
        except ValueError as ex:
            raise FormatPatternError(format_pattern, str(ex))

    @staticmethod
    def is_used(key: str, by: str) -> bool:
        """
        Check if a format string uses the given key.

        :param key: Key to check for.
        :param by: Format string to check.
        :return: `True` if the key is used in the given format string.
        """
        formatter = Formatter()
        for _, field_name, *_ in formatter.parse(by):
            if field_name == key:
                return True
        return False


def _merge_parts(parts: tuple[str, ...]) -> str:
    return ".".join(parts)


class PreserveFormat:
    def __init__(self, key: str) -> None:
        self._key = key

    def __format__(self, format_spec: str) -> str:
        if format_spec:
            return f"{{{self._key}:{format_spec}}}"
        return f"{{{self._key}}}"
