"""Installs the common Python package"""

from setuptools import setup, find_packages


# Load __version__ from file:
with open("cubeserver_common/_version.py", "r", encoding="utf-8") as version_file:
      exec(version_file.read())

# Metadata:
VERSION: str = __version__
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
            'Flask-Login>=0.6.1'
      ]
     )
