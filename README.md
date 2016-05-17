Experimental Glue VisPy plugin
==============================

[![Build Status](https://travis-ci.org/glue-viz/glue-3d-viewer.svg)](https://travis-ci.org/glue-viz/glue-3d-viewer?branch=master)
[![Build status](https://ci.appveyor.com/api/projects/status/1gov2vtuesjnij69/branch/master?svg=true)](https://ci.appveyor.com/project/astrofrog/glue-3d-viewer/branch/master)


Requirements
------------

Note that this plugin requires [Glue](http://glueviz.org/) and
[PyOpenGL](http://pyopengl.sourceforge.net/) to be installed - see [this
page](http://glueviz.org/en/latest/installation.html) for instructions on
installing Glue. PyOpenGL should get installed automatically when you install
the plugin (see below).

While this plugin uses VisPy, for now we bundle our own version of VisPy since
we rely on some recently added features, so you do not need to install VisPy
separately.

Installing
----------

To install the latest stable version of the plugin, you can do:

    pip install glue-vispy-viewers
    
or you can install the latest developer version from the git repository using:

    pip install https://github.com/glue-viz/glue-3d-viewer/archive/master.zip
    
This will auto-register the plugin with Glue. Now simply start up Glue, open a
data cube, drag it onto the main canvas, then select '3D viewer'.

Testing
-------

To run the tests, do:

    py.test glue_vispy_viewers

at the root of the repository. This requires the [pytest](http://pytest.org)
module to be installed.
