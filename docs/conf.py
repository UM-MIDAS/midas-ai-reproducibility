# conf.py — MIDAS Reproducible & Accessible AI Handbook
import os

if os.environ.get('READTHEDOCS') == 'True':
    html_context = {
        'output_path': os.path.join(os.environ.get('READTHEDOCS_OUTPUT', ''), 'html')
    }

# -- Project info -----------------------------------------------------
project = 'MIDAS Reproducible and Accessible AI'
copyright = '2026, Michigan Institute for Data and AI in Society'
author = 'MIDAS Research Team'
version = '0.3.0'
release = '0.3.0'

# -- General config ---------------------------------------------------
extensions = [
    "myst_parser",
    "sphinxcontrib.bibtex",
]

bibtex_bibfiles = ['references.bib']
bibtex_default_style = 'unsrt'
bibtex_reference_style = 'author_year'
# Numeric labels restart on each chapter's bibliography; that is intended.
suppress_warnings = ['bibtex.duplicate_label']

myst_enable_extensions = ["colon_fence", "deflist", "substitution", "tasklist"]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- HTML output ------------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["accessibility.css"]
html_title = "MIDAS Reproducible and Accessible AI"
