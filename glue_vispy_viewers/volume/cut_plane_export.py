from math import ceil
import numpy as np

from vispy import gloo
from vispy.gloo import FrameBuffer, RenderBuffer
from vispy.visuals.shaders import Function, ModularProgram

from glue_vispy_viewers.volume.shaders import CUT_PLANE_VERT_SHADER, get_cut_plane_frag_shader
from glue_vispy_viewers.volume.viewer_state import cutting_plane_polygon


def _polygon_to_voxel_space(polygon, bounds, resolution):
    mins = np.array([b[0] for b in bounds], dtype=float)
    maxs = np.array([b[1] for b in bounds], dtype=float)
    ranges = maxs - mins
    return (np.asarray(polygon, dtype=float) - mins) / ranges * resolution


def _polygon_normal(polygon):
    """Unit normal of a planar polygon using Newell's method."""
    nxt = np.roll(polygon, -1, axis=0)
    normal = np.array([
        np.sum((polygon[:, 1] - nxt[:, 1]) * (polygon[:, 2] + nxt[:, 2])),
        np.sum((polygon[:, 2] - nxt[:, 2]) * (polygon[:, 0] + nxt[:, 0])),
        np.sum((polygon[:, 0] - nxt[:, 0]) * (polygon[:, 1] + nxt[:, 1])),
    ])
    return normal / np.linalg.norm(normal)


def render_cut_plane_image(
    viewer_state,
    multivol,
):
    volumes = multivol.volumes
    frag_shader = get_cut_plane_frag_shader(volumes, clipped=multivol._clip_data)
    program = ModularProgram(CUT_PLANE_VERT_SHADER, frag_shader)
    program['a_position'] = np.array([[-1, -1], [1, -1], [-1, 1], [1, 1]], dtype=np.float32)
    texture0 = multivol.textures[0]
    program.frag['sampler_type'] = texture0.glsl_sampler_type
    program.frag['sample'] = texture0.glsl_sample

    for info in volumes.values():
        index = info['index']
        program['u_volumetex_{0}'.format(index)] = multivol.textures[index]
        cmap = info.get('cut_plane_cmap')
        if cmap is not None:
            program.frag['cut_plane_cmap{0:d}'.format(index)] = Function(cmap.glsl_map)

        program['u_enabled_{0}'.format(index)] = \
            multivol.shared_program['u_enabled_{0}'.format(index)]

    for uniform in ('u_clip_min', 'u_clip_max', 'u_cut_plane_image_bgcolor'):
        program[uniform] = multivol.shared_program[uniform]

    polygon = cutting_plane_polygon(viewer_state)
    bounds = (
        (viewer_state.x_min, viewer_state.x_max),
        (viewer_state.y_min, viewer_state.y_max),
        (viewer_state.z_min, viewer_state.z_max),
    )
    polygon = _polygon_to_voxel_space(
        polygon=polygon,
        bounds=bounds,
        resolution=viewer_state.resolution
    )
    stretches = np.array([
        viewer_state.x_stretch,
        viewer_state.y_stretch,
        viewer_state.z_stretch,
    ])
    scale = viewer_state.aspect * stretches
    scale /= scale.max()
    polygon *= scale
    centroid = polygon.mean(axis=0)
    normal = _polygon_normal(polygon)

    # Pick an in-plane "horizontal" axis.
    # Use z unless the plane is (nearly) perpendicular to z,
    # in which case (z x normal) vanishes and we fall back to y
    tmp = np.array((0, 0, 1), dtype=float)
    if abs(normal @ tmp) > 0.999:
        tmp = np.array((0, 1, 0), dtype=float)
    u_axis = np.cross(tmp, normal)
    u_axis /= np.linalg.norm(u_axis)
    v_axis = np.cross(u_axis, normal)
    v_axis /= np.linalg.norm(v_axis)

    relative = polygon - centroid
    u_coords = relative @ u_axis
    v_coords = relative @ v_axis
    u_min, u_max = u_coords.min(), u_coords.max()
    v_min, v_max = v_coords.min(), v_coords.max()
    width = ceil(u_max - u_min)
    height = ceil(v_max - v_min)

    center_u = 0.5 * (u_min + u_max)
    center_v = 0.5 * (v_min + v_max)

    center = centroid + center_u * u_axis + center_v * v_axis
    origin = center - 0.5 * (u_axis * width + v_axis * height)
    origin /= scale
    u_axis = u_axis * width / scale
    v_axis = v_axis * height / scale
    program['u_plane_origin'] = origin.astype(np.float32)
    program['u_plane_u_axis'] = u_axis.astype(np.float32)
    program['u_plane_v_axis'] = v_axis.astype(np.float32)
    program['u_shape'] = multivol._vol_shape

    color = RenderBuffer((height, width, 4))
    fbo = FrameBuffer(color=color)

    with fbo:
        gloo.set_viewport(0, 0, width, height)
        gloo.clear(color=(0, 0, 0, 0))
        # We don't need/want to blend or depth test for exporting an image
        gloo.set_state(blend=False, depth_test=False, cull_face=False)
        program.draw('triangle_strip')
        data = fbo.read()
        return data[::-1]
