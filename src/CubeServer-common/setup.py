"""Installs the common Python package"""

from setuptools import setup, find_packages


# Load __version__ from file:
with open("cubeserver_common/_version.py", "r", encoding="utf-8") as version_file:
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
      'Classes common to both the api and the webapp'
)

# Setup:
setup(name='CubeServer-common',
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHORS,
      url=GITHUB_URL,
      packages=find_packages(),
      install_requires=[
            'Flask>=2.1.2,<3.0',
            'Flask-PyMongo>=2.3.0,<3.0',
            'Flask-Login>=0.6.1',
            'better-profanity>=0.7.0',
            'bcrypt>=4.0.0,<5.0',
            'jsonpickle>=3.0.1,<4.0',
            'PyYAML>=6.0,<7.0',
            'pytest>=7.3.1,<8.0'
      ]
     )
