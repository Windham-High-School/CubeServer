"""Metadata for the entirety of CubeServer,
   for use wherever.
"""

__all__ = ["SERVER_NAME", "LICENSE", "LICENSE_FULL", "AUTHORS"]

from ._license import __license__ as LICENSE
from ._license import __full_license__ as LICENSE_FULL

SERVER_NAME = "CubeServer 2023-24 Edition"

AUTHORS: dict = {
    "Joseph R. Freeston": {
        "role": "The Architect",
        "contributions": "Primary CubeServer Developer\nLead software developer 2022-2023",
        "link": "https://github.com/snorklerjoe",
    },
    "Heather Brayer": {
        "role": "Contributor",
        "contributions": "Graphic Design",
        "link": "https://github.com/avocadoheather",
    },
    "Greg Kindrat": {
        "role": "Contributor",
        "contributions": "Graphic Design Assistant",
        "link": "",
    },
    "Julia Miller": {
        "role": "Contributor",
        "contributions": "Graphic Design Assistant",
        "link": "",
    },
    "Ryan Burbo": {
        "role": "Contributor",
        "contributions": "Graphic Design Assistant",
        "link": "",
    },
    "Lucas Tousignant": {
        "role": "Contributor",
        "contributions": "Cube Guinea Pig",
        "link": "",
    },
}
