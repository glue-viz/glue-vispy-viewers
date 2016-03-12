# This file implements a IsosurfaceVisual class that includes workarounds for
# the following VisPy bugs:
#
# https://github.com/vispy/vispy/pull/1179
# https://github.com/vispy/vispy/pull/1180
#
# It is derived from the original code for IsosurfaceVisual in
# vispy.visuals.isosurface, which is released under a BSD license included here:
#
# ===========================================================================
# Vispy is licensed under the terms of the (new) BSD license:
#
# Copyright (c) 2015, authors of Vispy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of Vispy Development Team nor the names of its
#   contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ===========================================================================
#
# This modified version is released under the BSD license given in the LICENSE
# file in this repository.

from __future__ import division

import numpy as np

from vispy.visuals.mesh import MeshVisual
from vispy.geometry.isosurface import isosurface
from vispy.color import Color
from vispy.scene.visuals import create_visual_node


# Find out if we are using the original or new drawing API
from vispy.visuals.isosurface import IsosurfaceVisual as VispyIsosurfaceVisual
HAS_PREPARE_DRAW = hasattr(VispyIsosurfaceVisual, '_prepare_draw')
del VispyIsosurfaceVisual


class IsosurfaceVisual(MeshVisual):
    """Displays an isosurface of a 3D scalar array.

    Parameters
    ----------
    data : ndarray | None
        3D scalar array.
    level: float | None
        The level at which the isosurface is constructed from *data*.

    Notes
    -----
    """
    def __init__(self, data=None, level=None, vertex_colors=None,
                 face_colors=None, color=(0.5, 0.5, 1, 1), **kwargs):
        self._data = None
        self._level = level
        self._vertex_colors = vertex_colors
        self._face_colors = face_colors
        self._color = Color(color)

        # We distinguish between recomputing and just changing the visual
        # properties - in the latter case we don't recompute the faces.
        self._vertices_cache = None
        self._faces_cache = None
        self._recompute = True
        self._update_meshvisual = True

        MeshVisual.__init__(self, **kwargs)
        if data is not None:
            self.set_data(data)

    @property
    def level(self):
        """ The threshold at which the isosurface is constructed from the
        3D data.
        """
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        self._recompute = True
        self.update()

    def set_data(self, data=None, vertex_colors=None, face_colors=None,
                 color=None):
        """ Set the scalar array data

        Parameters
        ----------
        data : ndarray
            A 3D array of scalar values. The isosurface is constructed to show
            all locations in the scalar field equal to ``self.level``.
        vertex_colors : array-like | None
            Colors to use for each vertex.
        face_colors : array-like | None
            Colors to use for each face.
        color : instance of Color
            The color to use.
        """
        # We only change the internal variables if they are provided
        if data is not None:
            self._data = data
            self._recompute = True
        if vertex_colors is not None:
            self._vertex_colors = vertex_colors
            self._update_meshvisual = True
        if face_colors is not None:
            self._face_colors = face_colors
            self._update_meshvisual = True
        if color is not None:
            self._color = Color(color)
            self._update_meshvisual = True
        self.update()

    def _update_mesh_visual(self):

        if self._data is None or self._level is None:
            return False

        if self._recompute:
            self._vertices_cache, self._faces_cache = isosurface(np.ascontiguousarray(self._data),
                                                                 self._level)
            self._recompute = False
            self._update_meshvisual = True

        if self._update_meshvisual:
            MeshVisual.set_data(self,
                                vertices=self._vertices_cache,
                                faces=self._faces_cache,
                                vertex_colors=self._vertex_colors,
                                face_colors=self._face_colors,
                                color=self._color)
            self._update_meshvisual = False

    if HAS_PREPARE_DRAW:
        def _prepare_draw(self, view):
            self._update_mesh_visual()
            return MeshVisual._prepare_draw(self, view)
    else:
        def draw(self, transforms):
            self._update_mesh_visual()
            return MeshVisual.draw(self, transforms)


Isosurface = create_visual_node(IsosurfaceVisual)
