Glue plugin for 3D viewers using VisPy
======================================

|Actions Status| |Coverage Status|

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

If you use the Anaconda Python Distribution, you can install this plugin
with::

    conda install -c glueviz glue-vispy-viewers

To install the latest stable version of the plugin, you can do::

    pip install glue-vispy-viewers

or you can install the latest developer version from the git repository
using::

    pip install git+https://github.com/glue-viz/glue-vispy-viewers.git

This will auto-register the plugin with Glue. Now simply start up Glue,
open a data cube, drag it onto the main canvas, then select '3D viewer'.

Testing
-------

To run the tests, do::

    py.test glue_vispy_viewers

at the root of the repository. This requires the
`pytest <http://pytest.org>`__ module to be installed.

Using the isosurface viewer
---------------------------

The isosurface viewer is currently still unstable - to enable it, put
the following in a file called ``config.py`` file in your current
working directory::

    from glue_vispy_viewers.isosurface import setup as setup_isosurface
    setup_isosurface()

.. |Actions Status| image:: https://github.com/glue-viz/glue-vispy-viewers/workflows/CI%20Workflows/badge.svg
    :target: https://github.com/glue-viz/glue-vispy-viewers/actions
    :alt: Glue's GitHub Actions CI Status
.. |Coverage Status| image:: https://codecov.io/gh/glue-viz/glue-vispy-viewers/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/glue-viz/glue-vispy-viewers
