Glue plugin for 3D viewers using VisPy
======================================

Requirements
------------

Note that this plugin requires `Glue <http://glueviz.org/>`__ and
`PyOpenGL <http://pyopengl.sourceforge.net/>`__ to be installed - see
`this page <http://glueviz.org/en/latest/installation.html>`__ for
instructions on installing Glue. PyOpenGL should get installed
automatically when you install the plugin (see below).

While this plugin uses VisPy, for now we bundle our own version of VisPy
since we rely on some recently added features, so you do not need to
install VisPy separately.

Installing
----------

If you use conda, you can install this plugin with::

    conda install -c conda-forge glue-vispy-viewers

or using pip::

    pip install glue-vispy-viewers

This will auto-register the plugin with Glue. Now simply start up Glue,
open a data cube, drag it onto the main canvas, then select one of the
3D viewer choices.

Testing
-------

To run the tests, do::

    pytest glue_vispy_viewers

at the root of the repository. This requires the
`pytest <http://pytest.org>`__ module to be installed.
