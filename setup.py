#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
vispy_volume=vispy_volume:setup
"""

setup(name='glue-3d-viewer',
      version="0.1.dev0",
      description = "Experimental VisPy plugin for glue",
      packages = find_packages(),
      package_data={'': ['*.ui'], '': ['*.png']},
      entry_points=entry_points
    )
