"""Installs the webapp Python package"""

from setuptools import setup, find_packages

setup(name='app',
      version='0.0.1',
      description='Web app for software to manage, store, score, and publish data'
                  'received from Wifi-equipped microcontrollers for a school contest',
      author='Joseph R. Freeston',
      url='https://github.com/snorklerjoe/CubeServer',
      packages=find_packages(),
      install_requires=[
            'Flask>=2.1.2,<3.0',
            'Flask-PyMongo>=2.3.0,<3.0',
            'pymongo-model>=2.0.2',
            'better-profanity>=0.7.0',
            'Flask-WTF>=1.0.1',
            'Flask-Bootstrap>=3.3',
            'uptime>=3.0.0',
            'Flask-Table>=0.5.0'
      ]
     )
