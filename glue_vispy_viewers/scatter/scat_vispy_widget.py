from __future__ import absolute_import, division, print_function

import sys

import numpy as np
from glue.external.qt import QtGui
from vispy import scene, app, gloo
from vispy import gloo
from vispy.util.transforms import perspective, translate, rotate


__all__ = ['QtScatVispyWidget']



class QtScatVispyWidget(QtGui.QWidget):

    def __init__(self, parent=None):

        super(QtScatVispyWidget, self).__init__(parent=parent)

        vert ="""
        #version 120

        // Uniforms
        // ------------------------------------
        uniform mat4 u_model;
        uniform mat4 u_view;
        uniform mat4 u_projection;
        uniform float u_linewidth;
        uniform float u_antialias;
        uniform float u_size;

        // Attributes
        // ------------------------------------
        attribute vec3  a_position;
        attribute vec4  a_fg_color;
        attribute vec4  a_bg_color;
        attribute float a_size;

        // Varyings
        // ------------------------------------
        varying vec4 v_fg_color;
        varying vec4 v_bg_color;
        varying float v_size;
        varying float v_linewidth;
        varying float v_antialias;

        void main (void) {
            v_size = a_size * u_size;
            v_linewidth = u_linewidth;
            v_antialias = u_antialias;
            v_fg_color  = a_fg_color;
            v_bg_color  = a_bg_color;
            gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
            gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
        }
        """


        frag = """
        #version 120

        // Constants
        // ------------------------------------


        // Varyings
        // ------------------------------------
        varying vec4 v_fg_color;
        varying vec4 v_bg_color;
        varying float v_size;
        varying float v_linewidth;
        varying float v_antialias;

        // Functions
        // ------------------------------------

        // ----------------
        float disc(vec2 P, float size)
        {
            float r = length((P.xy - vec2(0.5,0.5))*size);
            r -= v_size/2;
            return r;
        }

        // ----------------
        float arrow_right(vec2 P, float size)
        {
            float r1 = abs(P.x -.50)*size + abs(P.y -.5)*size - v_size/2;
            float r2 = abs(P.x -.25)*size + abs(P.y -.5)*size - v_size/2;
            float r = max(r1,-r2);
            return r;
        }

        // ----------------
        float ring(vec2 P, float size)
        {
            float r1 = length((gl_PointCoord.xy - vec2(0.5,0.5))*size) - v_size/2;
            float r2 = length((gl_PointCoord.xy - vec2(0.5,0.5))*size) - v_size/4;
            float r = max(r1,-r2);
            return r;
        }

        // ----------------
        float clober(vec2 P, float size)
        {
            const float PI = 3.14159265358979323846264;
            const float t1 = -PI/2;
            const vec2  c1 = 0.2*vec2(cos(t1),sin(t1));
            const float t2 = t1+2*PI/3;
            const vec2  c2 = 0.2*vec2(cos(t2),sin(t2));
            const float t3 = t2+2*PI/3;
            const vec2  c3 = 0.2*vec2(cos(t3),sin(t3));

            float r1 = length((gl_PointCoord.xy- vec2(0.5,0.5) - c1)*size);
            r1 -= v_size/3;
            float r2 = length((gl_PointCoord.xy- vec2(0.5,0.5) - c2)*size);
            r2 -= v_size/3;
            float r3 = length((gl_PointCoord.xy- vec2(0.5,0.5) - c3)*size);
            r3 -= v_size/3;
            float r = min(min(r1,r2),r3);
            return r;
        }

        // ----------------
        float square(vec2 P, float size)
        {
            float r = max(abs(gl_PointCoord.x -.5)*size,
                          abs(gl_PointCoord.y -.5)*size);
            r -= v_size/2;
            return r;
        }

        // ----------------
        float diamond(vec2 P, float size)
        {
            float r = abs(gl_PointCoord.x -.5)*size + abs(gl_PointCoord.y -.5)*size;
            r -= v_size/2;
            return r;
        }

        // ----------------
        float vbar(vec2 P, float size)
        {
            float r1 = max(abs(gl_PointCoord.x -.75)*size,
                           abs(gl_PointCoord.x -.25)*size);
            float r3 = max(abs(gl_PointCoord.x -.5)*size,
                           abs(gl_PointCoord.y -.5)*size);
            float r = max(r1,r3);
            r -= v_size/2;
            return r;
        }

        // ----------------
        float hbar(vec2 P, float size)
        {
            float r2 = max(abs(gl_PointCoord.y -.75)*size,
                           abs(gl_PointCoord.y -.25)*size);
            float r3 = max(abs(gl_PointCoord.x -.5)*size,
                           abs(gl_PointCoord.y -.5)*size);
            float r = max(r2,r3);
            r -= v_size/2;
            return r;
        }

        // ----------------
        float cross(vec2 P, float size)
        {
            float r1 = max(abs(gl_PointCoord.x -.75)*size,
                           abs(gl_PointCoord.x -.25)*size);
            float r2 = max(abs(gl_PointCoord.y -.75)*size,
                           abs(gl_PointCoord.y -.25)*size);
            float r3 = max(abs(gl_PointCoord.x -.5)*size,
                           abs(gl_PointCoord.y -.5)*size);
            float r = max(min(r1,r2),r3);
            r -= v_size/2;
            return r;
        }


        // Main
        // ------------------------------------
        void main()
        {
            float size = v_size +2*(v_linewidth + 1.5*v_antialias);
            float t = v_linewidth/2.0-v_antialias;

            float r = disc(gl_PointCoord, size);
            // float r = square(gl_PointCoord, size);
            // float r = ring(gl_PointCoord, size);
            // float r = arrow_right(gl_PointCoord, size);
            // float r = diamond(gl_PointCoord, size);
            // float r = cross(gl_PointCoord, size);
            // float r = clober(gl_PointCoord, size);
            // float r = hbar(gl_PointCoord, size);
            // float r = vbar(gl_PointCoord, size);


            float d = abs(r) - t;
            if( r > (v_linewidth/2.0+v_antialias))
            {
                discard;
            }
            else if( d < 0.0 )
            {
               gl_FragColor = v_fg_color;
            }
            else
            {
                float alpha = d/v_antialias;
                alpha = exp(-alpha*alpha);
                if (r > 0)
                    gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
                else
                    gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
            }
        }
        """

        # Prepare canvas
        self.canvas = app.Canvas(keys='interactive', show=False)
        self.canvas.size = [600, 400]
        self.canvas.measure_fps()

        # TODO: OpenGL code doesn't work now; If you want to use gloo without vispy.app, use a gloo.context.FakeCanvas.
        gloo.set_state('translucent', clear_color='white')
        gloo.gl.use_gl('gl2 debug')

        # Prepare canvas.program and related parameters
        self.canvas.program = gloo.Program(vert, frag)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = np.eye(4, dtype=np.float32)
        self.translate = 20  # This is used to set the initial size :-)
        self.view = translate((0, 0, -self.translate)) #Is there anything like self.view.translate?

        # Prepare data and subsets
        self.data = None

        # Set parameters for timer
        self.timer_dt = 1.0/60
        self.timer_t = 0.0
        self.timer = app.Timer(self.timer_dt)
        self.timer.connect(self.on_timer)

        # Prepare for mouse event and rotate
        self.is_dragging = False
        self.is_mouse_pressed = False
        self.theta, self.phi = 0, 0

        self.prev_phi = 0.0
        self.prev_theta = 0.0
        self.prev_timer_t = 0

        self.rotate_theta_speed = 0.0
        self.rotate_phi_speed = 0.0

        # Connect events
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        self.canvas.events.draw.connect(self.on_draw)
        self.canvas.events.resize.connect(self.on_resize)
        self.canvas.events.mouse_press.connect(self.on_mouse_press)
        self.canvas.events.mouse_move.connect(self.on_mouse_move)
        self.canvas.events.mouse_release.connect(self.on_mouse_release)

    def set_data(self, data):
        self.data = data

    # TODO: Add subset functionality
    def set_subsets(self, subsets):
        self.subsets = subsets

    # TODO: Customize the data component to general styles
    # Set canvas.program according to loading_data
    def set_program(self):
        if self.data is None:
            return None
        else:
            n = len(self.data.get_component('x_gal').data)
            P = np.zeros((n,3), dtype=np.float32)

            X, Y, Z =  P[:,0],P[:,1],P[:,2]
            X[...] = self.data.get_component('x_gal').data
            Y[...] = self.data.get_component('y_gal').data
            Z[...] = self.data.get_component('z_gal').data

            # Dot size determination according to the mass - *2 for larger size
            S = np.zeros(n)
            S[...] = 5* self.data.get_component('mass').data**(1./3)/1.e1


            # Wrap the data into a package
            data = np.zeros(n, [('a_position', np.float32, 3),
                                ('a_size',     np.float32, 1),
                                ('a_bg_color', np.float32, 4),
                                ('a_fg_color', np.float32, 4)])

            data['a_bg_color'] = np.random.uniform(0.85, 1.00, (n, 4))
            data['a_fg_color'] = 0, 0, 0, 1
            data['a_position'] = P
            data['a_size'] = S

            u_linewidth = 1.0
            u_antialias = 1.0

            self.canvas.program.bind(gloo.VertexBuffer(data))

            self.canvas.program['u_linewidth'] = u_linewidth
            self.canvas.program['u_antialias'] = u_antialias
            self.canvas.program['u_model'] = self.model
            self.canvas.program['u_view'] = self.view
            self.canvas.program['u_size'] = 5 / self.translate

            print('data is:', data)
            self.timer.start()

    def on_timer(self, event):
        self.timer_t += self.timer_dt # keep track on the current time
        self.theta += self.rotate_theta_speed
        self.phi += self.rotate_phi_speed
        self.model = np.eye(4, dtype=np.float32)
        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                            rotate(self.phi, (0, 1, 0)))
        self.canvas.program['u_model'] = self.model
        self.update()

    # Set projection for canvas.program
    def set_projection(self):
        gloo.set_viewport(0, 0, self.canvas.physical_size[0], self.canvas.physical_size[1])
        self.projection = perspective(45.0, self.canvas.size[0] /
                                      float(self.canvas.size[1]), 1.0, 1000.0)
        self.canvas.program['u_projection'] = self.projection

    def on_resize(self, event):
        self.set_projection()

    def on_draw(self, event):
        # gloo.clear()
        # self.canvas.program.draw(mode='points')
        gloo.gl.glClear(gloo.gl.GL_COLOR_BUFFER_BIT | gloo.gl.GL_DEPTH_BUFFER_BIT)
        # gloo.clear(color=True, depth=True)
        self.canvas.program.draw(gloo.gl.GL_POINTS)
        # self.canvas.update()

    def on_paint(self, event):
        gloo.gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.program.draw(gloo.gl.GL_POINTS)

    def on_mouse_wheel(self, event):
        self.translate -= event.delta[1]
        self.translate = max(2, self.translate)
        self.view = translate((0, 0, -self.translate))

        self.canvas.program['u_view'] = self.view
        self.canvas.program['u_size'] = 5 / self.translate
        self.canvas.update()

    def on_mouse_press(self, event):
        self.canvas.prev_cursor_x, self.canvas.prev_cursor_y = event.pos
        self.canvas.dragging_marked = False
        self.is_mouse_pressed = True

    def on_mouse_move(self, event):
        if event.is_dragging:
            self.is_dragging = True
            x, y = event.pos
            dx = x-self.canvas.prev_cursor_x
            dy = y-self.canvas.prev_cursor_y
            self.phi += float(dx)/x*180
            self.theta += float(dy)/y*180

            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))

            self.canvas.prev_cursor_x, self.canvas.prev_cursor_y = event.pos
            self.prev_timer_t = self.timer_t
            self.canvas.program['u_model'] = self.model
            self.canvas.update()

    def on_mouse_release(self, event):
        self.is_dragging = False
        self.is_mouse_pressed = False
