"""Sphinx configuration for GDX Aerospace documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath("../packages/aerounits/src"))
sys.path.insert(0, os.path.abspath("../packages/aerocalc/src"))

project = "GDX Aerospace"
copyright = "2026, GDX Tech Co. Ltd"
author = "GDX Tech Co. Ltd"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "myst_parser",
]

myst_enable_extensions = ["dollarmath", "colon_fence"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = []

autodoc_typehints = "description"
napoleon_google_docstring = False
napoleon_numpy_docstring = True
