"""Installs the Beacon Server Python package"""

from setuptools import setup, find_packages


# Load __version__ from file:
with open("cubeserver_beaconserver/_version.py", "r", encoding="utf-8") as version_file:
      exec(version_file.read())

# Metadata:
VERSION: str = __version__
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
            'APScheduler>=3.9.1,<4.0'
      ]
     )
