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

from __future__ import absolute_import, division, print_function

try:
    from textwrap import indent
except ImportError:  # Python < 3.5
    def indent(text, prefix):
        return '\n'.join(prefix + line for line in text.splitlines())

from ..extern.vispy.visuals.volume import VERT_SHADER

# Fragment shader
FRAG_SHADER = """
// uniforms
{declarations}
uniform vec3 u_shape;
uniform float u_downsample;
uniform float u_relative_step_size;
uniform vec4 u_bgcolor;

uniform int u_clipped = 0;
uniform vec3 u_clip_min;
uniform vec3 u_clip_max;

//varyings
// varying vec3 v_texcoord;
varying vec3 v_position;
varying vec4 v_nearpos;
varying vec4 v_farpos;

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

    // Now we have the starting position on the front surface
    vec3 front = v_position + view_ray * distance;

    // Decide how many steps to take
    int nsteps = int(-distance / (u_relative_step_size * u_downsample) + 0.5);
    if(nsteps < 1) discard;

    // Get starting location and step vector in texture coordinates
    vec3 step = ((v_position - front) / u_shape) / nsteps;
    vec3 start_loc = front / u_shape;

    float val;

    {before_loop}

    // This outer loop seems necessary on some systems for large
    // datasets. Ugly, but it works ...
    vec3 loc = start_loc;
    int iter = 0;

    // We avoid putting this if statement in the loop for performance

    if (u_downsample > 1.) {{

        // In the case where we are downsampling we use a step size that is
        // random to avoid artifacts in the output. This appears to be fast
        // enough to still make the downsampling worth it.

        while (iter < nsteps) {{
            for (iter=iter; iter<nsteps; iter++)
            {{

                if (u_clipped == 1) {{
                    if(loc.r > u_clip_min.r && loc.r < u_clip_max.r &&
                       loc.g > u_clip_min.g && loc.g < u_clip_max.g &&
                       loc.b > u_clip_min.b && loc.b < u_clip_max.b) {{
                   {in_loop}
                    }}
                }} else {{
                    {in_loop}
                }}

                // Advance location deeper into the volume
                loc += (0.5 + rand(loc)) * step;

            }}
        }}

    }} else {{

        while (iter < nsteps) {{
            for (iter=iter; iter<nsteps; iter++)
            {{

                if (u_clipped == 1) {{
                    if(loc.r > u_clip_min.r && loc.r < u_clip_max.r &&
                       loc.g > u_clip_min.g && loc.g < u_clip_max.g &&
                       loc.b > u_clip_min.b && loc.b < u_clip_max.b) {{
                   {in_loop}
                    }}
                }} else {{
                    {in_loop}
                }}

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

        total_color = u_bgcolor;

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


def get_shaders(n_volume_max):
    """
    Get the fragment shader code, supporting a maximum of ``n_volume_max``
    simultaneous textures and colormaps.
    """

    declarations = ""
    before_loop = ""
    in_loop = ""
    after_loop = ""

    for i in range(n_volume_max):

        # Global declarations
        declarations += "uniform $sampler_type u_volumetex_{0:d};\n".format(i)
        declarations += "uniform int u_enabled_{0:d};\n".format(i)
        declarations += "uniform float u_weight_{0:d};\n".format(i)
        declarations += "uniform int u_multiply_{0:d};\n".format(i)

        # Declarations before the raytracing loop
        before_loop += "float max_val_{0:d} = 0;\n".format(i)

        # Calculation inside the main raytracing loop

        multiply_code = "  if (u_multiply_{0:d} >= 0) {{\n".format(i)
        for j in range(n_volume_max):
            multiply_code += "    if (u_multiply_{0:d} == {1:d}) {{ val *= $sample(u_volumetex_{1:d}, loc).g; }}\n".format(i, j)
        multiply_code += "  }\n"

        in_loop += ("if (u_enabled_{i:d} == 1) {{\n"
                    "  val = $sample(u_volumetex_{i:d}, loc).g;\n"
                    "{multiply_code}"
                    "  max_val_{i:d} = max(val, max_val_{i:d});\n}}\n").format(i=i, multiply_code=multiply_code)

        # Calculation after the main loop

        after_loop += ("if (u_enabled_{0:d} == 1) {{\n"
                       "  color = $cmap{0:d}(max_val_{0:d});\n"
                       "  color.a *= u_weight_{0:d};\n"
                       "  total_color += color.a * color;\n"
                       "  max_alpha = max(color.a, max_alpha);\n"
                       "  count += color.a;\n}}\n").format(i)

    # Code esthetics
    before_loop = indent(before_loop, " " * 4).strip()
    in_loop = indent(in_loop, " " * 12).strip()
    after_loop = indent(after_loop, " " * 4).strip()

    return VERT_SHADER, FRAG_SHADER.format(declarations=declarations,
                                           before_loop=before_loop,
                                           in_loop=in_loop,
                                           after_loop=after_loop)


if __name__ == "__main__":  # pragma: nocover
    print(get_shaders(6)[1])
