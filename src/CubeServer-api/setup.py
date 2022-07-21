"""Installs the API Server Python package"""

from setuptools import setup, find_packages


# Load __version__ from file:
with open("cubeserver_api/_version.py", "r", encoding="utf-8") as version_file:
      exec(version_file.read())

# Metadata:
VERSION: str = __version__
"""Version string"""

AUTHORS: str = "Joseph R. Freeston"
"""A comma-separated list of contributors"""

GITHUB_URL: str = "https://github.com/snorklerjoe/CubeServer"
"""A URL to the source code and info on GitHub"""

DESCRIPTION = (
      'An API for logging data into the database.'
)

# Setup:
setup(name='CubeServer-api',
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHORS,
      url=GITHUB_URL,
      packages=find_packages(),
      install_requires=[
            'Flask>=2.1.2,<3.0',
            'Flask-RESTful>=0.3.9,<1.0',
            'CubeServer-common'
      ]
     )
