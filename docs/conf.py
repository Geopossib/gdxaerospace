"""Sphinx configuration for GDX Aerospace documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath("../packages/aerounits/src"))
sys.path.insert(0, os.path.abspath("../packages/aerocalc/src"))
sys.path.insert(0, os.path.abspath("../packages/airfoilpy/src"))
sys.path.insert(0, os.path.abspath("../packages/wingtools/src"))
sys.path.insert(0, os.path.abspath("../packages/dragpy/src"))
sys.path.insert(0, os.path.abspath("../packages/compressibleflow/src"))
sys.path.insert(0, os.path.abspath("../packages/shockpy/src"))
sys.path.insert(0, os.path.abspath("../packages/boundarylayer/src"))
sys.path.insert(0, os.path.abspath("../packages/aeroprop/src"))
sys.path.insert(0, os.path.abspath("../packages/rocketperf/src"))
sys.path.insert(0, os.path.abspath("../packages/nozzleanalysis/src"))
sys.path.insert(0, os.path.abspath("../packages/combustionpy/src"))
sys.path.insert(0, os.path.abspath("../packages/turbomachpy/src"))
sys.path.insert(0, os.path.abspath("../packages/plasmathrust/src"))
sys.path.insert(0, os.path.abspath("../packages/electricprop/src"))
sys.path.insert(0, os.path.abspath("../packages/plume3d/src"))
sys.path.insert(0, os.path.abspath("../packages/plasmaspace/src"))
sys.path.insert(0, os.path.abspath("../packages/attitude3d/src"))
sys.path.insert(0, os.path.abspath("../packages/flightdyn/src"))
sys.path.insert(0, os.path.abspath("../packages/aircraftsim/src"))
sys.path.insert(0, os.path.abspath("../packages/guidancepy/src"))
sys.path.insert(0, os.path.abspath("../packages/navigationpy/src"))
sys.path.insert(0, os.path.abspath("../packages/autopilotpy/src"))
sys.path.insert(0, os.path.abspath("../packages/kalmanflight/src"))
sys.path.insert(0, os.path.abspath("../packages/orbitpy/src"))
sys.path.insert(0, os.path.abspath("../packages/tletools/src"))
sys.path.insert(0, os.path.abspath("../packages/satprop/src"))
sys.path.insert(0, os.path.abspath("../packages/groundtrack/src"))
sys.path.insert(0, os.path.abspath("../packages/missionpy/src"))
sys.path.insert(0, os.path.abspath("../packages/constellationpy/src"))
sys.path.insert(0, os.path.abspath("../packages/sattelemetry/src"))
sys.path.insert(0, os.path.abspath("../packages/aeromaterials/src"))
sys.path.insert(0, os.path.abspath("../packages/aerostruct/src"))
sys.path.insert(0, os.path.abspath("../packages/stresspy/src"))
sys.path.insert(0, os.path.abspath("../packages/sparcalc/src"))
sys.path.insert(0, os.path.abspath("../packages/bucklingpy/src"))
sys.path.insert(0, os.path.abspath("../packages/fatiguepy/src"))
sys.path.insert(0, os.path.abspath("../packages/compositepy/src"))
sys.path.insert(0, os.path.abspath("../packages/laminatepy/src"))
sys.path.insert(0, os.path.abspath("../packages/aerothermal/src"))
sys.path.insert(0, os.path.abspath("../packages/aerocfd/src"))
sys.path.insert(0, os.path.abspath("../packages/aerodata/src"))
sys.path.insert(0, os.path.abspath("../packages/uavpy/src"))
sys.path.insert(0, os.path.abspath("../packages/aerovision/src"))
sys.path.insert(0, os.path.abspath("../packages/rockettraj/src"))
sys.path.insert(0, os.path.abspath("../packages/aeroopt/src"))
sys.path.insert(0, os.path.abspath("../packages/gdxaerospace/src"))

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
