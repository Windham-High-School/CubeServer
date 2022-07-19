"""Installs the webapp Python package"""

from setuptools import setup, find_packages


# Metadata:
VERSION: str = "0.0.1rc"
"""Version string"""

AUTHORS: str = "Joseph R. Freeston"
"""A comma-separated list of contributors"""

GITHUB_URL: str = "https://github.com/snorklerjoe/CubeServer"
"""A URL to the source code and info on GitHub"""

DESCRIPTION = (
      'Web app for software to manage, store, score, and publish data'
      'received from Wifi-equipped microcontrollers for a school contest'
)

# Setup:
setup(name='app',
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
            'is-safe-url'
      ]
     )
