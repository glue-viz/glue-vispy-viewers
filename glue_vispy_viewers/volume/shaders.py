# This file implements a fragment shader that can be used to visualize multiple
# volumes simultaneously. It is derived from the original fragment shader in
# vispy.visuals.volume, which is releaed under a BSD license included here:
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

try:
    from textwrap import indent
except ImportError:  # Python < 3.5
    def indent(text, prefix):
        return '\n'.join(prefix + line for line in text.splitlines())

# Vertex shader
VERT_SHADER = """
attribute vec3 a_position;
uniform vec3 u_shape;
varying vec3 v_position;
varying vec4 v_nearpos;
varying vec4 v_farpos;
void main() {
    v_position = a_position;
    // Project local vertex coordinate to camera position. Then do a step
    // backward (in cam coords) and project back. Voila, we get our ray vector.
    vec4 pos_in_cam = $viewtransformf(vec4(v_position, 1));
    // intersection of ray and near clipping plane (z = -1 in clip coords)
    pos_in_cam.z = -pos_in_cam.w;
    v_nearpos = $viewtransformi(pos_in_cam);
    // intersection of ray and far clipping plane (z = +1 in clip coords)
    pos_in_cam.z = pos_in_cam.w;
    v_farpos = $viewtransformi(pos_in_cam);
    gl_Position = $transform(vec4(v_position, 1.0));
}
"""

# Fragment shader
FRAG_SHADER = """
// uniforms
{declarations}
uniform vec3 u_shape;
uniform float u_downsample;
uniform vec4 u_bgcolor;

uniform vec3 u_clip_min;
uniform vec3 u_clip_max;

//varyings
// varying vec3 v_texcoord;
varying vec3 v_position;
varying vec4 v_nearpos;
varying vec4 v_farpos;

// A cutting plane defined as ax + by + cz + d = 0 where the vector below is (a, b, c).
// u_cutting_plane_enabled is a 0/1 flag so we can skip the computation (and avoid
// the division-by-zero that happens when a ray is parallel to the plane) when no
// cut is set.
uniform int u_cutting_plane_enabled;
uniform vec3 u_cutting_plane_abc;
uniform float u_cutting_plane_d;

// Opacity of the slice image rendered on the cut surface; 0 disables it.
// The image is only drawn when the camera sits on the +normal side of the
// plane (i.e. the side that has been removed by the cut), so it appears on
// the visible face of the remaining volume rather than hiding behind it.
uniform float u_cut_plane_image_opacity;

uniform vec4 u_cut_plane_image_bgcolor;

// uniforms for lighting. Hard coded until we figure out how to do lights
const vec4 u_ambient = vec4(0.2, 0.4, 0.2, 1.0);
const vec4 u_diffuse = vec4(0.8, 0.2, 0.2, 1.0);
const vec4 u_specular = vec4(1.0, 1.0, 1.0, 1.0);
const float u_shininess = 40.0;

//varying vec3 lightDirs[1];

// global holding view direction in local coordinates
vec3 view_ray;


// for some reason, this has to be the last function in order for the
// filters to be inserted in the correct place...

float rand(vec3 co) {{
    float a = 12.9898;
    float b = 78.233;
    float c = 43758.5453;
    float dt= dot(vec2(co.x, co.y + co.z) ,vec2(a,b));
    float sn= mod(dt,3.14);
    return fract(sin(sn) * c);
}}

void main() {{
    vec3 farpos = v_farpos.xyz / v_farpos.w;
    vec3 nearpos = v_nearpos.xyz / v_nearpos.w;

    // Calculate unit vector pointing in the view direction through this
    // fragment.
    view_ray = normalize(farpos.xyz - nearpos.xyz);

    // Compute the distance to the front surface or near clipping plane
    float distance = dot(nearpos-v_position, view_ray);
    distance = max(distance, min((-0.5 - v_position.x) / view_ray.x,
                            (u_shape.x - 0.5 - v_position.x) / view_ray.x));
    distance = max(distance, min((-0.5 - v_position.y) / view_ray.y,
                            (u_shape.y - 0.5 - v_position.y) / view_ray.y));
    distance = max(distance, min((-0.5 - v_position.z) / view_ray.z,
                            (u_shape.z - 0.5 - v_position.z) / view_ray.z));

    // Restrict the sampling segment to the "kept" side of the cutting plane.
    // The kept side is defined in volume coordinates as
    //     dot(p, u_cutting_plane_abc) + u_cutting_plane_d < 0
    // i.e. the half-space opposite the plane normal. Defining the kept side
    // this way (rather than implicitly via the ray direction) makes the
    // result invariant under camera rotation: rotating the view shows the
    // same kept material from a different angle, rather than flipping which
    // material is visible.
    float exit_distance = 0.0;
    float plane_t = 0.0;          // ray parameter where the cutting plane crosses, if any
    int plane_image_visible = 0;  // whether the cut-surface image should be drawn
    if (u_cutting_plane_enabled == 1) {{
        float original_distance = distance;
        float v0 = dot(v_position, u_cutting_plane_abc) + u_cutting_plane_d;
        float vdir = dot(view_ray, u_cutting_plane_abc);
        if (abs(vdir) < 1e-6) {{
            if (v0 > 0.0) discard;
        }} else {{
            float t_plane = -v0 / vdir;
            if (vdir > 0.0) {{
                exit_distance = min(exit_distance, t_plane);
            }} else {{
                distance = max(distance, t_plane);
            }}
            // The plane image is meaningful only where the plane actually
            // crosses this ray inside the cube, AND the camera is on the
            // removed side -- otherwise the plane sits behind the volume
            // material from the viewer's perspective and shouldn't show.
            if (t_plane > original_distance && t_plane < 0.0) {{
                float q_camera = dot(nearpos, u_cutting_plane_abc) + u_cutting_plane_d;
                if (q_camera > 0.0) {{
                    plane_t = t_plane;
                    plane_image_visible = 1;
                }}
            }}
        }}
    }}
    if (exit_distance <= distance) discard;

    // Now we have the starting position on the front surface
    vec3 front = v_position + view_ray * distance;
    vec3 back = v_position + view_ray * exit_distance;

    // Decide how many steps to take
    int nsteps = int((exit_distance - distance) / u_downsample + 0.5);
    if(nsteps < 1) discard;

    // Get starting location and step vector in texture coordinates
    vec3 step = ((back - front) / u_shape) / nsteps;
    vec3 start_loc = front / u_shape;

    float val;

    // This outer loop seems necessary on some systems for large
    // datasets. Ugly, but it works ...
    vec3 loc = start_loc;
    int iter = 0;

    {before_loop}

    // We avoid putting this if statement in the loop for performance

    if (u_downsample > 1.) {{

        // In the case where we are downsampling we use a step size that is
        // random to avoid artifacts in the output. This appears to be fast
        // enough to still make the downsampling worth it.

        while (iter < nsteps) {{
            for (iter=iter; iter<nsteps; iter++)
            {{

                {in_loop}

                // Advance location deeper into the volume
                loc += (0.5 + rand(loc)) * step;

            }}
        }}

    }} else {{

        while (iter < nsteps) {{
            for (iter=iter; iter<nsteps; iter++)
            {{

                {in_loop}

                // Advance location deeper into the volume
                loc += step;

            }}
        }}

    }}


    float count = 0;
    vec4 color = vec4(0., 0., 0., 0.);
    vec4 total_color = vec4(0., 0., 0., 0.);
    float max_alpha = 0;

    {after_loop}

    if(count > 0) {{

        total_color /= count;
        total_color.a = max_alpha;

        // Due to issues with transparency in Qt5, we need to convert the color
        // to a flattened version without transparency, so we do alpha blending
        // with the background and set alpha to 1:
        total_color.r = total_color.r * total_color.a + u_bgcolor.r * (1 - total_color.a);
        total_color.g = total_color.g * total_color.a + u_bgcolor.g * (1 - total_color.a);
        total_color.b = total_color.b * total_color.a + u_bgcolor.b * (1 - total_color.a);
        total_color.a = 1.;

    }} else {{

        // For this it seems we can get away with using transparency (which we need
        // to make sure axes/ticks/labels aren't hidden)
        total_color = vec4(0, 0, 0, 0);

    }}

    // Cut-surface image overlay. Samples each layer once at the plane intersection,
    // colormaps it through the layer's cutting plane colormap function,
    // then composites the result over the MIP result at the user-controlled opacity.
    if (u_cut_plane_image_opacity > 0.0 && plane_image_visible == 1) {{
        vec3 plane_loc = (v_position + view_ray * plane_t) / u_shape;
        vec4 plane_total_color = u_cut_plane_image_bgcolor;
        vec4 plane_color = vec4(0., 0., 0., 0.);
        float plane_count = 0.;
        float plane_val;

        {plane_sample}

        if (plane_count > 0.) {{
            plane_total_color /= plane_count;
            // Premultiply rgb by the sampled colormap alpha so the value shows
            // as brightness on the slice: Fixed-colour layers encode the data
            // only in alpha, and for colourmaps the alpha tracks the value too,
            // so out-of-range (and low) values fade to dark rather than leaving
            // transparent holes in the slice.
            plane_total_color.rgb *= plane_total_color.a;
            // The slider value is the final overlay alpha so that at
            // opacity == 1 the slice fully covers the volume behind it.
            float a = u_cut_plane_image_opacity;
            total_color.rgb = mix(total_color.rgb, plane_total_color.rgb, a);
            total_color.a = max(total_color.a, a);
        }}
    }}

    gl_FragColor = total_color;

    /* Set depth value - from visvis TODO
    int iter_depth = int(maxi);
    // Calculate end position in world coordinates
    vec4 position2 = vertexPosition;
    position2.xyz += ray*shape*float(iter_depth);
    // Project to device coordinates and set fragment depth
    vec4 iproj = gl_ModelViewProjectionMatrix * position2;
    iproj.z /= iproj.w;
    gl_FragDepth = (iproj.z+1.0)/2.0;
    */
}}
"""


def get_plane_sample_shader(volumes, clipped=False):
    """
    Build the GLSL that samples each enabled volume at `plane_loc` (a vec3 in
    normalized [0,1]^3 texture space) and accumulates into `plane_total_color`
    / `plane_count`.

    This is shared extracted into its own function so that it can be reused
    """
    plane_sample = ""

    for label in sorted(volumes):

        index = volumes[label]['index']

        plane_sample += "if(u_enabled_{0:d} == 1) {{\n\n".format(index)

        if clipped:
            plane_sample += ("if(plane_loc.r > u_clip_min.r && plane_loc.r < u_clip_max.r &&\n"
                             "   plane_loc.g > u_clip_min.g && plane_loc.g < u_clip_max.g &&\n"
                             "   plane_loc.b > u_clip_min.b && plane_loc.b < u_clip_max.b) {\n\n")

        plane_sample += "plane_val = $sample(u_volumetex_{0:d}, plane_loc).g;\n".format(index)

        if volumes[label].get('multiply') is not None:
            index_other = volumes[volumes[label]['multiply']]['index']
            plane_sample += (
                "if (plane_val != 0) {{ plane_val *= $sample(u_volumetex_{0:d}, plane_loc).g; }}\n"
                .format(index_other))
        # Note: we deliberately don't multiply by u_weight_N for the slice
        # sample. The MIP layer weight is a "how much does this layer fade
        # into the rest" knob meant for the volume render; the slice already
        # has the user's opacity slider for that, and pulling u_weight in
        # would dim Linear-mode slices.
        plane_sample += "plane_color = $cut_plane_cmap{0:d}(plane_val);\n".format(index)
        # Unlike the volume MIP pass, the slice image should appear across the
        # whole cut surface, not only where the colormap alpha (i.e. the volume
        # opacity) is non-zero. Count every in-bounds sample and average the
        # colourmap colours directly so values at or below v_min still render
        # (as dark pixels via the premultiply) instead of leaving holes.
        plane_sample += ("plane_total_color.rgb = "
                         "mix(plane_total_color.rgb, plane_color.rgb, plane_color.a);\n")
        plane_sample += "plane_count += 1.0;\n\n"

        if clipped:
            plane_sample += "}\n\n"

        plane_sample += "}\n\n"

    return plane_sample


def get_frag_shader(volumes, clipped=False, n_volume_max=5):
    """
    Get the fragment shader code - we use the shader_program object to determine
    which layers are enabled and therefore what to include in the shader code.
    """

    declarations = ""
    before_loop = ""
    in_loop = ""
    after_loop = ""
    plane_sample = ""

    for index in range(n_volume_max):
        declarations += "uniform $sampler_type u_volumetex_{0:d};\n".format(index)
        before_loop += "dummy = $sample(u_volumetex_{0:d}, loc).g;\n".format(index)

    declarations += "uniform $sampler_type dummy1;\n"
    declarations += "float dummy;\n"

    for label in sorted(volumes):

        index = volumes[label]['index']

        # Global declarations
        declarations += "uniform float u_weight_{0:d};\n".format(index)
        declarations += "uniform int u_enabled_{0:d};\n".format(index)

        # Declarations before the raytracing loop
        before_loop += "float max_val_{0:d} = 0;\n".format(index)

        # Calculation inside the main raytracing loop

        in_loop += "if(u_enabled_{0:d} == 1) {{\n\n".format(index)

        if clipped:
            in_loop += ("if(loc.r > u_clip_min.r && loc.r < u_clip_max.r &&\n"
                        "   loc.g > u_clip_min.g && loc.g < u_clip_max.g &&\n"
                        "   loc.b > u_clip_min.b && loc.b < u_clip_max.b) {\n\n")

        in_loop += "// Sample texture for layer {0}\n".format(label)
        in_loop += "val = $sample(u_volumetex_{0:d}, loc).g;\n".format(index)

        if volumes[label].get('multiply') is not None:
            index_other = volumes[volumes[label]['multiply']]['index']
            in_loop += ("if (val != 0) {{ val *= $sample(u_volumetex_{0:d}, loc).g; }}\n"
                        .format(index_other))

        in_loop += "max_val_{0:d} = max(val, max_val_{0:d});\n\n".format(index)

        if clipped:
            in_loop += "}\n\n"

        in_loop += "}\n\n"

        # Calculation after the main loop

        after_loop += "// Compute final color for layer {0}\n".format(label)
        after_loop += ("color = $cmap{0:d}(max_val_{0:d});\n"
                       "color.a *= u_weight_{0:d};\n"
                       "total_color += color.a * color;\n"
                       "max_alpha = max(color.a, max_alpha);\n"
                       "count += color.a;\n\n").format(index)

    plane_sample = get_plane_sample_shader(volumes, clipped=clipped)

    if not clipped:
        before_loop += "\nfloat val3 = u_clip_min.g + u_clip_max.g;\n\n"

    # Code esthetics
    before_loop = indent(before_loop, " " * 4).strip()
    in_loop = indent(in_loop, " " * 16).strip()
    after_loop = indent(after_loop, " " * 4).strip()
    plane_sample = indent(plane_sample, " " * 8).strip()

    return FRAG_SHADER.format(declarations=declarations,
                              before_loop=before_loop,
                              in_loop=in_loop,
                              after_loop=after_loop,
                              plane_sample=plane_sample)


CUT_PLANE_VERT_SHADER = """
attribute vec2 a_position;
uniform vec3 u_plane_origin;
uniform vec3 u_plane_u_axis;
uniform vec3 u_plane_v_axis;
uniform vec3 u_shape;
varying vec3 v_plane_loc;

void main() {
    vec2 uv = a_position * 0.5 + 0.5;  // [-1, 1] -> [0, 1]
    vec3 p = u_plane_origin + u_plane_u_axis * uv.x + u_plane_v_axis * uv.y;
    v_plane_loc = p / u_shape;
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

CUT_PLANE_FRAG_SHADER = """
{declarations}
uniform vec3 u_clip_min;
uniform vec3 u_clip_max;
uniform vec4 u_cut_plane_image_bgcolor;

varying vec3 v_plane_loc;

void main() {{
    vec3 plane_loc = v_plane_loc;

    if (plane_loc.r < 0.0 || plane_loc.r > 1.0 ||
        plane_loc.g < 0.0 || plane_loc.g > 1.0 ||
        plane_loc.b < 0.0 || plane_loc.b > 1.0) {{
        gl_FragColor = vec4(0., 0., 0., 0.);
        return;
    }}

    vec4 plane_total_color = u_cut_plane_image_bgcolor;
    vec4 plane_color = vec4(0., 0., 0., 0.);
    float plane_count = 0.;
    float plane_val;

    {plane_sample}

    if (plane_count > 0.) {{
        plane_total_color /= plane_count;
        plane_total_color.rgb *= plane_total_color.a;
    }}

    gl_FragColor = plane_total_color;
    gl_FragColor.a = 1.0;
}}
"""


def get_cut_plane_frag_shader(volumes, clipped=False):
    """
    Fragment shader for the standalone cutting-plane render
    """

    declarations = ""
    for label in sorted(volumes):
        index = volumes[label]['index']
        declarations += "uniform $sampler_type u_volumetex_{0:d};\n".format(index)
        declarations += "uniform int u_enabled_{0:d};\n".format(index)

    plane_sample = get_plane_sample_shader(volumes, clipped=clipped)
    plane_sample = indent(plane_sample, " " * 4).strip()

    return CUT_PLANE_FRAG_SHADER.format(declarations=declarations,
                                        plane_sample=plane_sample)


def main():

    volumes = {}
    volumes['banana'] = {'index': 3, 'enabled': True}
    volumes['apple'] = {'index': 1, 'multiply': None, 'enabled': True}
    volumes['apple'] = {'index': 1, 'multiply': 'banana', 'enabled': True}

    print(get_frag_shader(volumes))


if __name__ == "__main__":  # pragma: nocover
    main()
