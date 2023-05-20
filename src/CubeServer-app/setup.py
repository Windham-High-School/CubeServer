"""Installs the webapp Python package"""

from setuptools import setup, find_packages


# Load __version__ from file:
with open("cubeserver_app/_version.py", "r", encoding="utf-8") as version_file:
      exec(version_file.read())

# Metadata:
VERSION: str = __version__
"""Version string"""

AUTHORS: str = "Original Architect: Joseph R. Freeston. Maintained by The CubeServer Authors"
"""A comma-separated list of contributors"""

GITHUB_URL: str = "https://github.com/snorklerjoe/CubeServer"
"""A URL to the source code and info on GitHub"""

DESCRIPTION = (
      'Web app for software to manage, store, score, and publish data'
      'received from Wifi-equipped microcontrollers for a school contest'
)

# Setup:
setup(name='CubeServer-app',
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHORS,
      url=GITHUB_URL,
      packages=find_packages(),
      install_requires=[
            'Flask>=2.1.2,<3.0',
            'Flask-PyMongo>=2.3.0,<3.0',
            'better-profanity>=0.7.0',
            'Flask-WTF>=1.0.1',
            'wtforms[email]',
            'Flask-Bootstrap>=3.3',
            'uptime>=3.0.0',
            'Flask-Table>=0.5.0',
            'Flask-Login>=0.6.1',
            'is-safe-url',
            'CubeServer-common',
            'Flask-APScheduler>=1.12.4,<2.0',
            'pytest>=7.3.1,<8.0'
      ]
     )
