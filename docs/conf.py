# Configuration file for the Sphinx documentation builder.

import os
import sys
import yaml

# -- Path setup --------------------------------------------------------------

sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('../src/CubeServer-api'))
sys.path.insert(0, os.path.abspath('../src/CubeServer-app'))
sys.path.insert(0, os.path.abspath('../src/CubeServer-common'))

# -- Project information -----------------------------------------------------

project = 'CubeServer'
author = 'Joseph R. Freeston'

# The full version, including alpha/beta/rc tags
with open('../version.txt', 'r') as f:
    version = f.read().strip()
release = version

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# -- Options for autodoc -----------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'private-members': True,
    'special-members': '__init__',
    'exclude-members': '__weakref__',
}

autodoc_typehints = 'description'

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Options for autosectionlabel --------------------------------------------

autosectionlabel_prefix_document = True

# -- Options for viewcode ----------------------------------------------------

viewcode_follow_imported_members = True

# -- Copyright notice --------------------------------------------------------

import datetime

now = datetime.datetime.now()
year = now.year

copyright = f"""
{year} CubeServer Contributors
"""
