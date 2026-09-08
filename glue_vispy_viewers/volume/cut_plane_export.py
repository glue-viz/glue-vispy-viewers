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

        program['u_enabled_{0}'.format(index)] = multivol.shared_program['u_enabled_{0}'.format(index)]

    for uniform in ('u_clip_min', 'u_clip_max', 'u_cut_plane_image_bgcolor'):
        program[uniform] = multivol.shared_program[uniform]

    polygon = cutting_plane_polygon(viewer_state)
    bounds = (
        (viewer_state.x_min, viewer_state.x_max),
        (viewer_state.y_min, viewer_state.y_max),
        (viewer_state.z_min, viewer_state.z_max),
    )
    polygon = _polygon_to_voxel_space(polygon=polygon, bounds=bounds, resolution=viewer_state.resolution)
    polygon *= viewer_state.aspect
    centroid = polygon.mean(axis=0)
    v0 = polygon[0] - centroid
    v1 = polygon[len(polygon) // 2] - centroid
    normal = np.cross(v0, v1)
    normal /= np.linalg.norm(normal)

    tmp = np.array((0, 0, 1), dtype=float)
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
    origin /= viewer_state.aspect
    u_axis = u_axis * width / viewer_state.aspect
    v_axis = v_axis * height / viewer_state.aspect
    program['u_plane_origin'] = origin.astype(np.float32)
    program['u_plane_u_axis'] = u_axis.astype(np.float32)
    program['u_plane_v_axis'] = v_axis.astype(np.float32)
    program['u_shape'] = multivol._vol_shape

    color = RenderBuffer((height, width, 4))
    fbo = FrameBuffer(color=color)

    with fbo:
        gloo.set_viewport(0, 0, width, height)
        gloo.clear(color=(0, 0, 0, 0))
        program.draw('triangle_strip')
        data = fbo.read()
        return data[::-1]
