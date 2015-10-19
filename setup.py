#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
vispy_volume=glue_vispy_viewers.volume:setup
vispy_isosurface=glue_vispy_viewers.isosurface:setup
"""

setup(name='glue-vispy-viewers',
      version="0.1.dev0",
      description = "Experimental VisPy plugin for glue",
      packages = find_packages(),
      package_data={'glue_vispy_viewers.volume': ['*.ui'],
                    'glue_vispy_viewers.isosurface': ['*.ui']},
      entry_points=entry_points
    )
