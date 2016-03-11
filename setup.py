#!/usr/bin/env python

from __future__ import print_function

from setuptools import setup, find_packages

entry_points = """
[glue.plugins]
vispy_volume=glue_vispy_viewers.volume:setup
vispy_scatter=glue_vispy_viewers.scatter:setup
vispy_isosurface=glue_vispy_viewers.isosurface:setup
"""

with open('glue_vispy_viewers/version.py') as infile:
    exec(infile.read())

try:
    import pypandoc
    LONG_DESCRIPTION = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    with open('README.md') as infile:
        LONG_DESCRIPTION = infile.read()

setup(name='glue-vispy-viewers',
      version=__version__,
      description='Vispy-based viewers for Glue',
      long_description=LONG_DESCRIPTION,
      url="https://github.com/glue-viz/glue-3d-viewer",
      author='Penny Qian, Maxwell Tsai, and Thomas Robitaille',
      author_email='glueviz@gmail.com',
      packages = find_packages(),
      package_data={'glue_vispy_viewers.volume': ['*.ui'],
                    'glue_vispy_viewers.common': ['*.ui'],
                    'glue_vispy_viewers.isosurface': ['*.ui'],
                    'glue_vispy_viewers.scatter': ['*.ui']},
      entry_points=entry_points
    )
