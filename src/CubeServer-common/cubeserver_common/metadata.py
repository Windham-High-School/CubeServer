"""Metadata for the entirety of CubeServer,
   for use wherever.
"""

from yaml import safe_load
from .config import CONTRIBUTORS_YAML

__all__ = [
    'LICENSE',
    'LICENSE_FULL',
    'VERSION',
    'TIMESTAMP',
    'AUTHORS'
]

from ._license import __license__ as LICENSE
from ._license import __full_license__ as LICENSE_FULL
from ._version import __version__ as VERSION
from ._version import __timestamp__ as TIMESTAMP

AUTHORS: dict = safe_load(CONTRIBUTORS_YAML)
