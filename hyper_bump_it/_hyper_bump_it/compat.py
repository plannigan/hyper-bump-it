"""
Consolidate Python version compatibility code.
"""

import sys

# flake8: noqa: F401

if sys.version_info < (3, 11):
    from typing_extensions import (
        LiteralString as LiteralString,  # this supports python < 3.11
    )
else:
    from typing import (
        LiteralString as LiteralString,  # this is available in python 3.11+
    )
