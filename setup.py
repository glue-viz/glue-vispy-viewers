#!/usr/bin/env python

from __future__ import print_function

import os
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

# Define package data for our plugin

package_data = {'glue_vispy_viewers.volume': ['*.ui'],
                'glue_vispy_viewers.common': ['*.ui', '*.png'],
                'glue_vispy_viewers.isosurface': ['*.ui'],
                'glue_vispy_viewers.scatter': ['*.ui']}

# Include data for bundled version of VisPy.

package_data['glue_vispy_viewers.extern.vispy'] = [os.path.join('io', '_data', '*'),
                                                   os.path.join('html', 'static', 'js', '*'),
                                                   os.path.join('app', 'tests', 'qt-designer.ui')]

for subpackage in ['antialias', 'arrowheads', 'arrows', 'collections',
                   'colormaps', 'lines', 'markers', 'math', 'misc',
                   'transforms']:
    package_data['glue_vispy_viewers.extern.vispy.glsl.' + subpackage] = ['*.vert','*.frag', "*.glsl"]

setup(name='glue-vispy-viewers',
      version=__version__,
      description='Vispy-based viewers for Glue',
      long_description=LONG_DESCRIPTION,
      url="https://github.com/glue-viz/glue-3d-viewer",
      author='Penny Qian, Maxwell Tsai, and Thomas Robitaille',
      author_email='glueviz@gmail.com',
      packages = find_packages(),
      package_data=package_data,
      entry_points=entry_points,
      install_requires=['pyopengl']
    )
