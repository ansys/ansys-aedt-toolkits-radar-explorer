# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sphinx documentation configuration file."""

from datetime import datetime
import os
from pathlib import Path
import sys

from ansys_sphinx_theme import ansys_favicon
from ansys_sphinx_theme import ansys_logo_white
from ansys_sphinx_theme import ansys_logo_white_cropped
from ansys_sphinx_theme import get_version_match
from ansys_sphinx_theme import latex
from ansys_sphinx_theme import pyansys_logo_black
from ansys_sphinx_theme import watermark
from plotly.io._sg_scraper import plotly_sg_scraper
import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper
from sphinx.util import logging

os.environ["PYANSYS_VISUALIZER_DOC_MODE"] = "true"
pyvista.BUILDING_GALLERY = True
os.environ["PYVISTA_BUILDING_GALLERY"] = "true"
pyvista.OFF_SCREEN = True

root_path = str(Path(__file__).parent.parent.parent)
src_path = Path(root_path) / "src"
sys.path.insert(0, str(root_path))
sys.path.insert(0, str(src_path))
print("root_path:", root_path)
print("src_path:", str(src_path))

try:
    from ansys.aedt.toolkits.radar_explorer import __version__
except ImportError:  # pragma: no cover
    sys.path.append(root_path)

    sys.path.append(str(src_path))
    from ansys.aedt.toolkits.radar_explorer import __version__

logger = logging.getLogger(__name__)

# Sphinx event hooks


def check_pandoc_installed(app):
    """Ensure that pandoc is installed."""
    import pypandoc

    try:
        pandoc_path = pypandoc.get_pandoc_path()
        pandoc_dir = str(Path(pandoc_path).parent)
        if pandoc_dir not in os.environ["PATH"].split(os.pathsep):
            logger.info("Pandoc directory is not in $PATH.")
            os.environ["PATH"] += os.pathsep + pandoc_dir
            logger.info(f"Pandoc directory '{pandoc_dir}' has been added to $PATH")
    except OSError:
        logger.error("Pandoc was not found, please add it to your path or install pypandoc-binary")


def setup(app):
    app.connect("builder-inited", check_pandoc_installed)


os.environ["PYANSYS_VISUALIZER_HTML_BACKEND"] = "true"


print(__version__)
# Project information
project = "ansys-aedt-toolkits-radar-explorer"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", default="aedt.radar.explorer.toolkit.docs.pyansys.com")
switcher_version = get_version_match(__version__)
print(copyright)

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "ansys-aedt-toolkits-radar"

# specify the location of your GitHub repo
html_context = {
    "github_user": "ansys",
    "github_repo": "ansys-aedt-toolkits-radar-explorer",
    "github_version": "main",
    "doc_path": "doc/source",
}
html_theme_options = {
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/ansys-aedt-toolkits-radar-explorer",
    "navigation_with_keys": False,
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/issues",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Download documentation in PDF",
            "url": f"https://{cname}/version/{switcher_version}/_static/assets/download/ansys-aedt-toolkits-radar-explorer.pdf",  # noqa: E501
            "icon": "fa fa-file-pdf fa-fw",
        },
    ],
}

# Sphinx extensions
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_gallery.gen_gallery",
    "recommonmark",
    "numpydoc",
    "nbsphinx",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# Removing check on repo lines of code as using line numbers as anchor is not working
# linkcheck_ignore = [
#     "https://github.com/ansys/pyaedt-toolkits-antenna/blob/main/src/ansys/aedt/toolkits/antenna/ui/"
#     "actions.py#L165",
#     "https://github.com/ansys/pyaedt-toolkits-antenna/blob/main/src/ansys/aedt/toolkits/antenna/ui/"
#     "actions.py#L143",
# ]

# Add replace in RST files
github_releases_dl_url = "https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/download"
installer = "RCS-Explorer-Toolkit-Installer"
rst_epilog = f"""
.. |github_release_url| replace:: https://github.com/ansys/ansys-aedt-toolkits-radar-explorer/releases/tag/v{release}
.. |github_windows_installer| replace:: {github_releases_dl_url}/v{release}/{installer}.exe
.. |github_ubuntu_22_installer| replace:: {github_releases_dl_url}/v{release}/{installer}-ubuntu_22_04.zip
.. |github_ubuntu_24_installer| replace:: {github_releases_dl_url}/v{release}/{installer}-ubuntu_24_04.zip
"""

# static path
html_static_path = ["_static"]

html_css_files = [
    "custom.css",
]

html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Execute notebooks before conversion
nbsphinx_execute = "always"

# Allow errors to help debug.
nbsphinx_allow_errors = True

# Sphinx gallery customization

sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": ["examples"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples/gallery"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created.
    "doc_module": "ansys-aedt-toolkits-radar-explorer",
    "image_scrapers": (DynamicScraper(), "matplotlib", plotly_sg_scraper),
    "ignore_pattern": r"flycheck*|index\.rst|__init__\.py",
    "thumbnail_size": (350, 350),
    "remove_config_comments": True,
    "show_signature": False,
}

exclude_patterns = ["_build", "sphinx_boogergreen_theme_1", "Thumbs.db", ".DS_Store", "*.txt", "conf.py"]

# -- Options for LaTeX output ------------------------------------------------

# additional logos for the latex coverage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

os.environ["PYAEDT_NON_GRAPHICAL"] = "1"
