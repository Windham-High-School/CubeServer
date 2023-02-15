# Configuration file for the Sphinx documentation builder.

#import os
#import sys

from sphinx.ext.apidoc import main

# -- APIDOC
main(['../src/CubeServer-app/cubeserver_app/', '-o', './codedocs/cubeserver_app'])
main(['../src/CubeServer-api/cubeserver_api/', '-o', './codedocs/cubeserver_api'])
main(['../src/CubeServer-common/cubeserver_common/', '-o', './codedocs/cubeserver_common'])
main(['../src/CubeServer-beaconserver/cubeserver_beaconserver/', '-o', './codedocs/cubeserver_beaconserver'])

# -- Project information

project = 'CubeServer'
copyright = '2022-2023, Joseph R. Freeston'
author = 'Joseph R. Freeston'

#release = '0.1'
#version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'nbsphinx',
    'sphinx_rtd_theme'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

#sys.path.insert(0, os.path.abspath('../src/CubeServer-common'))
#sys.path.insert(0, os.path.abspath('../src/CubeServer-app'))
#sys.path.insert(0, os.path.abspath('../src/CubeServer-api'))
