import numpy as np
from echo import CallbackProperty, SelectionCallbackProperty

from glue.viewers.volume3d.viewer_state import VolumeViewerState3D

__all__ = ['Vispy3DVolumeViewerState', 'cutting_plane_polygon']


def _cube_extent(state):
    """Side length of the shader cube the cutting plane is defined in.

    The volume fragment shader's ``v_position`` spans ``0..u_shape`` on each
    axis, and ``u_shape`` is ``(resolution,) * 3`` (the fixed-resolution
    buffer size, independent of the underlying data shape). The cutting plane
    parameters are therefore computed relative to a cube whose side equals the
    current resolution rather than a fixed size.
    """
    return float(state.resolution)


def _axis_angles(axis):
    """Return ``(tilt, rotation)`` in radians for an axis-aligned cut.

    The normal is +x, +y or +z; the cube center sits on the kept side.
    """
    if axis == 'X':
        return np.pi / 2, 0.0
    if axis == 'Y':
        return np.pi / 2, np.pi / 2
    return 0.0, 0.0   # 'Z'


def cutting_plane_from_state(state):
    """Return the shader (a, b, c, d) tuple, or ``None`` if disabled.

    The cube extends 0..resolution in each shader coordinate. The plane's
    signed distance from the cube centre is moved linearly between
    ``+half_diagonal`` (depth=0, plane outside on the +normal side, nothing
    cut) and ``-half_diagonal`` (depth=1, plane outside on the -normal side,
    everything cut).
    """
    if not state.cut_enabled:
        return None
    if state.cut_mode == 'Simple':
        tilt, rotation = _axis_angles(state.cut_axis)
    else:
        tilt, rotation = state.cut_tilt, state.cut_rotation
    extent = _cube_extent(state)
    center = extent / 2.0
    half_diagonal = (3.0 ** 0.5) * center
    a = np.sin(tilt) * np.cos(rotation)
    b = np.sin(tilt) * np.sin(rotation)
    c = np.cos(tilt)
    offset = half_diagonal * (1.0 - 2.0 * state.cut_depth)
    d = -(a + b + c) * center - offset
    # Flipping an axis limit (max < min) reverses the data along that axis in
    # the volume texture, so reflect the plane across the axis (v -> extent - v)
    # to keep the cut on the same data side as the bounding box and axis ticks.
    if state.x_max < state.x_min:
        a, d = -a, d + extent * a
    if state.y_max < state.y_min:
        b, d = -b, d + extent * b
    if state.z_max < state.z_min:
        c, d = -c, d + extent * c
    if state.cut_flip:
        # Negate the whole plane equation: the same geometric plane, with the
        # kept and removed half-spaces swapped.
        a, b, c, d = -a, -b, -c, -d
    return float(a), float(b), float(c), float(d)


# Edge list for the 8-corner cube, where corner index ``i`` is
# (xmin if bit0 else xmax, ymin if bit1 else ymax, zmin if bit2 else zmax).
_CUBE_EDGES = ((0, 1), (2, 3), (4, 5), (6, 7),
               (0, 2), (1, 3), (4, 6), (5, 7),
               (0, 4), (1, 5), (2, 6), (3, 7))


def cutting_plane_polygon(state):
    """Polygon where the cutting plane intersects the data bounding box.

    Returns an ``(N, 3)`` array of vertices in data coordinates ordered
    around the centroid (suitable for drawing as a closed line strip),
    or ``None`` if the plane misses the box (or the state is disabled).
    """
    plane = cutting_plane_from_state(state)
    if plane is None:
        return None

    # Convert the shader plane (which lives in 0..extent v_position coords)
    # into data coords. With ``v_k = (k - k_min) * extent / (k_max - k_min)``
    # the equation ``a*vx + b*vy + c*vz + d = 0`` becomes
    # ``A*x + B*y + C*z + D = 0`` with the scaling below.
    a, b, c, d = plane
    extent = _cube_extent(state)
    rng_x = state.x_max - state.x_min
    rng_y = state.y_max - state.y_min
    rng_z = state.z_max - state.z_min
    if rng_x == 0 or rng_y == 0 or rng_z == 0:
        return None
    A = a * extent / rng_x
    B = b * extent / rng_y
    C = c * extent / rng_z
    D = d - A * state.x_min - B * state.y_min - C * state.z_min
    n = np.array([A, B, C])

    corners = np.array([(state.x_min if (i & 1) == 0 else state.x_max,
                         state.y_min if (i & 2) == 0 else state.y_max,
                         state.z_min if (i & 4) == 0 else state.z_max)
                        for i in range(8)])
    side = corners @ n + D

    points = []
    for i, j in _CUBE_EDGES:
        s0, s1 = side[i], side[j]
        if s0 * s1 < 0:
            t = s0 / (s0 - s1)
            points.append(corners[i] + t * (corners[j] - corners[i]))
        elif s0 == 0:
            points.append(corners[i])

    if len(points) < 3:
        return None

    points = np.asarray(points)
    centroid = points.mean(axis=0)
    # Build a 2D basis on the plane to sort vertices around the centroid.
    ref = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u = np.cross(n, ref)
    u /= np.linalg.norm(u)
    v = np.cross(n, u)
    diffs = points - centroid
    angles = np.arctan2(diffs @ v, diffs @ u)
    # Deduplicate vertices that coincide (e.g. when the plane passes through a
    # cube corner two edges report the same point).
    order = np.argsort(angles)
    ordered = points[order]
    keep = [ordered[0]]
    for p in ordered[1:]:
        if np.linalg.norm(p - keep[-1]) > 1e-6:
            keep.append(p)
    return np.asarray(keep)


class Vispy3DVolumeViewerState(VolumeViewerState3D):
    """Volume viewer state with vispy-only extensions.

    Subclasses ``glue.viewers.volume3d.viewer_state.VolumeViewerState3D``
    and adds attributes that only make sense for the vispy-based volume
    renderer, so they aren't visible from non-vispy frontends (notably
    ipyvolume) which would otherwise ignore them. If/when those become
    cross-frontend concepts they can be lifted into glue-core.
    """

    cut_enabled = CallbackProperty(False, docstring='Whether the cutting plane is active.')
    cut_mode = SelectionCallbackProperty(
        0, choices=['Simple', 'Advanced'],
        docstring='Simple (axis-aligned) or Advanced (free orientation).')
    cut_axis = SelectionCallbackProperty(
        2, choices=['X', 'Y', 'Z'],
        docstring='Axis perpendicular to the cutting plane in Simple mode.')
    cut_tilt = CallbackProperty(0.0, docstring='Polar angle of the plane normal, radians (0..pi).')
    cut_rotation = CallbackProperty(
        0.0, docstring='Azimuthal angle of the plane normal, radians (0..2*pi).')
    cut_depth = CallbackProperty(0.5, docstring='Depth of the cut, 0 (no cut) to 1 (full cut).')
    cut_flip = CallbackProperty(
        False, docstring='Whether to show the opposite side of the cutting plane.')
    cut_plane_image_opacity = CallbackProperty(
        0.0, docstring='Opacity of the slice image rendered on the cutting plane (0 = off).')
    cut_plane_image_bgcolor = CallbackProperty(
        "#000000", docstring='Base color of the cutting plane')

    def flip_cut(self):
        """Swap which side of the cutting plane is shown versus clipped.

        Toggles :attr:`cut_flip`, which negates the plane equation in
        ``cutting_plane_from_state`` so the kept and removed regions swap
        without moving the plane or touching the tilt, rotation, depth or
        mode. This works the same in Simple and Advanced mode.
        """
        self.cut_flip = not self.cut_flip

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # SelectionCallbackProperty stores choices per-instance via a WeakKeyDictionary
        # populated lazily on first ``get_choices`` lookup. Force the dictionary to be
        # populated now so the choices are bound to the instance (rather than only to
        # the class) and survive a round-trip through ``__setgluestate__``.
        Vispy3DVolumeViewerState.cut_mode.set_choices(self, ['Simple', 'Advanced'])
        Vispy3DVolumeViewerState.cut_axis.set_choices(self, ['X', 'Y', 'Z'])
