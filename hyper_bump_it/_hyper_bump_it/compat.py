"""
Consolidate Python version compatibility code.
"""
import sys

# flake8: noqa: F401

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias as TypeAlias  # this supports python < 3.10
else:
    from typing import TypeAlias as TypeAlias  # this is available in python 3.10+

if sys.version_info < (3, 11):
    from typing_extensions import (
        LiteralString as LiteralString,  # this supports python < 3.11
    )
else:
    from typing import (
        LiteralString as LiteralString,  # this is available in python 3.11+
    )
