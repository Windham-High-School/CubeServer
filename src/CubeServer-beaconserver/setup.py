"""Installs the Beacon Server Python package"""

from setuptools import setup, find_packages


# Load __version__ from file:
with open("cubeserver_beaconserver/_version.py", "r", encoding="utf-8") as version_file:
      exec(version_file.read())

assert '__version__' in locals(), "Missing version metadata- broken package."

if '__timestamp__' not in locals():
      raise RuntimeError("Could not find __timestamp__ in _version.py")

# Metadata:
VERSION: str = __version__  # type: ignore
"""Version string"""

AUTHORS: str = "Joseph R. Freeston"
"""A comma-separated list of contributors"""

GITHUB_URL: str = "https://github.com/snorklerjoe/CubeServer"
"""A URL to the source code and info on GitHub"""

DESCRIPTION = (
      'A server for managing/talking to the beacon'
)

# Setup:
setup(name='CubeServer-beaconserver',
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHORS,
      url=GITHUB_URL,
      packages=find_packages(),
      install_requires=[
            'CubeServer-common',
            'apscheduler>=3.9.1,<4.0',
            'pytest>=7.3.1,<8.0'
      ]
     )
