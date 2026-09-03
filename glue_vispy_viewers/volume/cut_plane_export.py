import numpy as np

from vispy import gloo
from vispy.gloo import Program, FrameBuffer, RenderBuffer
from vispy.visuals.shaders import Function

from glue_vispy_viewers.volume.shaders import CUT_PLANE_VERT_SHADER, get_cut_plane_frag_shader


def render_cut_plane_image(
    multivol,
    size=(512, 512),
    extent=None
):

    # GLSL setup
    volumes = multivol.volumes
    frag_shader = get_cut_plane_frag_shader(volumes, clipped=multivol._clip_data)
    program = Program(CUT_PLANE_VERT_SHADER, frag_shader)

    program['a_position'] = np.array([[-1, -1], [1, -1], [-1, 1], [1, 1]], dtype=np.float32)
    texture0 = multivol.textures[0]
    program.frag['sampler_type'] = texture0.glsl_sampler_type
    program.frag['sample'] = texture0.glsl_sample

    # Create a frame buffer
    color = RenderBuffer((size[1], size[0], 4))
    fbo = FrameBuffer(color=color)

    for label, info in volumes.items():
        index = info['index']
        program['u_volumetex_{0}'.format(index)] = multivol.textures[i]
        cmap = info.get('cut_plane_cmap')
        if cmap is not None:
            program.frag['cut_plane_cmap{0:d}'.format(index)] = Function(cmap.glsl_map)

        program['u_enabled_{0}'.format(index)] = multivol.shared_program['u_enabled_{0}'.format(index)]

    for uniform in ('u_clip_min', 'u_clip_max', 'u_cut_plane_image_bgcolor'):
        program[uniform] = multivol.shared_program[uniform]

    a, b, c = multivol.shared_program['u_cutting_plane_abc']
    d = multivol.shared_program['u_cutting_plane_d']

    normal = np.asarray((a, b, c), dtype=float)
    normal /= np.dot(normal, normal)
    point = - d * normal
    tmp = np.array((1, 0, 0), dtype=float)
    if abs(np.dot(tmp, normal)) > 0.9:
        tmp = np.array((0, 1, 0), dtype=float)
    u_axis = np.cross(normal, tmp)
    u_axis /= np.linalg.norm(u_axis)
    v_axis = np.cross(normal, u_axis)

    if extent is None:
        extent = float(np.linalg.norm(multivol._vol_shape))

    origin = point - u_axis * extent / 2 - v_axis * extent / 2
    program['u_plane_origin'] = origin.astype(np.float32)
    program['u_plane_u_axis'] = (u_axis * extent).astype(np.float32)
    program['u_plane_v_axis'] = (v_axis * extent).astype(np.float32)
    program['u_shape'] = multivol._vol_shape

    with fbo:
        gloo.set_viewport(0, 0, size[0], size[1])
        gloo.clear(color=(0, 0, 0, 0))
        program.draw('triangle_strip')
        return fbo.read()
