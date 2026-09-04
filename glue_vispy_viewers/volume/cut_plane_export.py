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


def _compute_export_size(plane_normal, plane_polygon, max_dimension=2048):
    normal = np.asarray(plane_normal, dtype=float)
    normal /= np.linalg.norm(normal)

    tmp = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(tmp, normal)) > 0.9:
        tmp = np.array([1.0, 0.0, 0.0])
    u_axis = np.cross(normal, tmp)
    u_axis /= np.linalg.norm(u_axis)
    v_axis = np.cross(normal, u_axis)

    polygon = np.asarray(plane_polygon, dtype=float)
    centroid = polygon.mean(axis=0)
    relative = polygon - centroid
    u_coords = relative @ u_axis
    v_coords = relative @ v_axis

    width = u_coords.max() - u_coords.min()
    height = v_coords.max() - v_coords.min()

    if width >= height:
        return (max_dimension, max(1, int(round(max_dimension * height / width))))
    else:
        return (max(1, int(round(max_dimension * width / height))), max_dimension)


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

    a, b, c = multivol.shared_program['u_cutting_plane_abc']

    normal = np.asarray((a, b, c), dtype=float)
    normal /= np.dot(normal, normal)
    tmp = np.array((0, 0, 1), dtype=float)
    if abs(np.dot(tmp, normal)) > 0.9:
        tmp = np.array((0, 1, 0), dtype=float)
    u_axis = np.cross(normal, tmp)
    u_axis /= np.linalg.norm(u_axis)
    v_axis = np.cross(normal, u_axis)
    u_axis *= -1

    polygon = cutting_plane_polygon(viewer_state)
    bounds = (
        (viewer_state.x_min, viewer_state.x_max),
        (viewer_state.y_min, viewer_state.y_max),
        (viewer_state.z_min, viewer_state.z_max),
    )
    polygon = _polygon_to_voxel_space(polygon=polygon, bounds=bounds, resolution=viewer_state.resolution)
    centroid = polygon.mean(axis=0)

    relative = polygon - centroid
    u_coords = relative @ u_axis
    v_coords = relative @ v_axis
    width = ceil(np.ptp(u_coords))
    height = ceil(np.ptp(v_coords))

    origin = centroid - 0.5 * (u_axis * width + v_axis * height)
    program['u_plane_origin'] = origin.astype(np.float32)
    program['u_plane_u_axis'] = (u_axis * width).astype(np.float32)
    program['u_plane_v_axis'] = (v_axis * height).astype(np.float32)
    program['u_shape'] = multivol._vol_shape

    color = RenderBuffer((height, width, 4))
    fbo = FrameBuffer(color=color)

    with fbo:
        gloo.set_viewport(0, 0, width, height)
        gloo.clear(color=(0, 0, 0, 0))
        program.draw('triangle_strip')
        data = fbo.read()
        return data[::-1]
