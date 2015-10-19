Experimental Glue VisPy plugin
==============================

[![Build Status](https://travis-ci.org/glue-viz/glue-3d-viewer.svg)](https://travis-ci.org/glue-viz/glue-3d-viewer?branch=master)
[![Build status](https://ci.appveyor.com/api/projects/status/1gov2vtuesjnij69/branch/master?svg=true)](https://ci.appveyor.com/project/astrofrog/glue-3d-viewer/branch/master)

Requirements
------------

Note that this plugin requires [Glue](http://glueviz.org/) and
[VisPy](http://vispy.org/) to be installed. Both can be installed with conda:

    conda install glueviz vispy

Installing
----------

To install the latest stable version of the plugin, you can do:

    pip install glue-vispy-viewers
    
or you can install the latest developer version from the git repository using:

    python setup.py install
    
This will auto-register the plugin with Glue. Now simply start up Glue, open a
data cube, drag it onto the main canvas, then select '3D viewer'.

Testing
-------

To run the tests, do:

    py.test glue_vispy_viewers

at the root of the repository. This requires the [pytest](http://pytest.org) module to be installed.
