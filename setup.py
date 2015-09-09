#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
vispy_volume=vispy_volume:setup
vispy_isosurface=vispy_isosurface:setup
"""

setup(name='glue-3d-viewer',
      version="0.1.dev0",
      description = "Experimental VisPy plugin for glue",
      # packages = find_packages(),
      packages = ['vispy_volume', 'vispy_isosurface'],
      package_data={'vispy_volume': ['*.ui'], 'vispy_isosurface': ['*.ui']},
      entry_points=entry_points
    )
