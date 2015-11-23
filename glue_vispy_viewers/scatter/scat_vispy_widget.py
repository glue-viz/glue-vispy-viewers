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


        # Initialize
        # gloo.set_state('translucent', clear_color='black')
        # gloo.glDisable(gloo.GL_DEPTH_TEST)
        # gloo.glEnable(gloo.GL_BLEND)
        # gloo.glBlendFunc(gloo.GL_SRC_ALPHA, gloo.GL_ONE) #_MINUS_SRC_ALPHA)

        # Prepare canvas
        self.canvas = app.Canvas(keys='interactive', show=False)
        self.canvas.size = [600, 400]
        self.canvas.measure_fps()

        # Set up a viewbox to display the image with interactive pan/zoom
        # self.view = self.canvas.central_widget.add_view()
        # self.view.border_color = 'red'
        # self.view.parent = self.canvas.scene
        self.view = np.eye(4,dtype=np.float32)



        # If you want to use gloo without vispy.app, use a gloo.context.FakeCanvas.

        gloo.set_state('translucent', clear_color='white')

        self.program = gloo.Program(vert, frag)
        gloo.gl.use_gl('gl2 debug')
        # self.program = gloo.Program(self.VERT_SHADER, self.FRAG_SHADER)
        self.model = np.eye(4,dtype=np.float32)
        self.projection = np.eye(4,dtype=np.float32)
        self.theta, self.phi = 0,0

        self.translate = 20  # For cute Penny: this is used to set the initial size :-)
        self.view = translate((0, 0, -self.translate)) #Is there anything like self.view.translate?

        self.data = None
        '''self.zoom_size = 0
        self.zoom_text_visual = self.add_text_visual()
        self.zoom_timer = app.Timer(0.2, connect=self.on_timer, start=False)

        # Add a 3D axis to keep us oriented
        # self.axis = scene.visuals.XYZAxis(parent=self.view.scene)
        # self.widget_axis_scale = [1, 1, 1]'''

        # self.program.bind(gloo.VertexBuffer(data))

        # self.program['u_size'] = 5./self.translate
        # self.program['u_model'] = self.model
        # self.program['u_view'] = self.view

        self.timer_dt = 1.0/60
        self.timer_t = 0.0
        self.timer = app.Timer(self.timer_dt)
        self.timer.connect(self.on_timer)

        self.is_dragging = False
        self.is_mouse_pressed = False

        self.prev_phi = 0.0
        self.prev_theta = 0.0
        self.prev_timer_t = 0

        self.rotate_theta_speed = 0.0
        self.rotate_phi_speed = 0.0

        # Connect events
        self.canvas.events.mouse_wheel.connect(self.on_mouse_wheel)
        self.canvas.events.draw.connect(self.on_draw)
        self.canvas.events.resize.connect(self.on_resize)

        # gl.glClearColor(0,0,0,1)
        # gl.glDisable(gl.GL_DEPTH_TEST)
        # gl.glEnable(gl.GL_BLEND)
        # gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE)

    # def on_initialize(self, event):
    #     gl.glClearColor(0,0,0,1)
    #     gl.glDisable(gl.GL_DEPTH_TEST)
    #     gl.glEnable(gl.GL_BLEND)
    #     gl.glBlendFunc (gl.GL_SRC_ALPHA, gl.GL_ONE) #_MINUS_SRC_ALPHA)
    #     Start the timer upon initialization.
        # self.timer.start()
        # print('Timer.start')

    def set_data(self, data):
        self.data = data

    # def set_frame_data(self,data):
    #     self.program.bind(gloo.VertexBuffer(data))

        print('Data bind!')

    def set_subsets(self, subsets):
        self.subsets = subsets

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
            S[...] = 5* self.data.get_component('mass').data**(1./3)/1.e5


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

            self.program.bind(gloo.VertexBuffer(data))

            self.program['u_linewidth'] = u_linewidth
            self.program['u_antialias'] = u_antialias
            self.program['u_model'] = self.model
            self.program['u_view'] = self.view
            self.program['u_size'] = 5 / self.translate

            print('data is:', data)
            self.timer.start()
            # return data

    def on_key_press(self, event):
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
                print('Press enter!')
            else:
                self.timer.start()

    def on_timer(self, event):
        self.timer_t += self.timer_dt # keep track on the current time
        self.theta += self.rotate_theta_speed
        self.phi += self.rotate_phi_speed
        self.model = np.eye(4, dtype=np.float32)
        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                            rotate(self.phi, (0, 1, 0)))
        self.program['u_model'] = self.model
        self.update()

    '''def set_projection(self):
        # width, height = event.size
        # gloo.glViewport(0, 0, width, height)
        # self.projection = perspective( 45.0, width/float(height), 1.0, 1000.0 )
        # self.program['u_projection'] = self.projection
        gloo.set_viewport(0, 0, self.canvas.physical_size[0], self.canvas.physical_size[1])
        self.projection = perspective(45.0, self.canvas.size[0] /
                                      float(self.canvas.size[1]), 1.0, 1000.0)
        self.program['u_projection'] = self.projection'''

    def on_mouse_wheel(self, event):
        self.translate -= event.delta[1]
        self.translate = max(2, self.translate)
        self.view = translate((0, 0, -self.translate))

        self.program['u_view'] = self.view
        self.program['u_size'] = 5 / self.translate
        self.canvas.update()

    # Now the resize works well
    def on_resize(self, event):
        gloo.set_viewport(0, 0, self.canvas.physical_size[0], self.canvas.physical_size[1])
        self.projection = perspective(45.0, self.size[0] /
                                      float(self.size[1]), 1.0, 1000.0)
        self.program['u_projection'] = self.projection

    def on_draw(self, event):
        # gloo.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # gloo.clear()
        # RuntimeError: Program validation error
        gloo.clear()
        self.program.draw(mode='points')


    # def on_paint(self, event):
    #     gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    #     self.program.draw(gl.GL_POINTS)

    '''def add_volume_visual(self):

        # TODO: need to implement the visualiation of the subsets in this method

        vol_data = self.get_data()
        # Create the volume visual and give default settings
        vol_visual = scene.visuals.Volume(vol_data, parent=self.view.scene, threshold=0.1, method='mip',
                                       emulate_texture=self.emulate_texture)
        # volume1.cmap = self.color_map

        trans = (-vol_data.shape[2]/2, -vol_data.shape[1]/2, -vol_data.shape[0]/2)
        _axis_scale = (vol_data.shape[2], vol_data.shape[1], vol_data.shape[0])
        vol_visual.transform = scene.STTransform(translate=trans)

        self.axis.transform = scene.STTransform(translate=trans, scale=_axis_scale)

        self.vol_visual = vol_visual
        self.widget_axis_scale = self.axis.transform.scale

    def add_text_visual(self):
        # Create the text visual to show zoom scale
        text = scene.visuals.Text('', parent=self.canvas.scene, color='white', bold=True, font_size=16)
        text.pos = [40, self.canvas.size[1]-40]
        return text

    def on_timer(self, event):
        self.zoom_text_visual.color = [1, 1, 1, float((7-event.iteration) % 8)/8]
        self.canvas.update()

    def on_resize(self, event):
        self.zoom_text_visual.pos = [40, self.canvas.size[1] - 40]

    def on_mouse_wheel(self, event):
        if self.view.camera.distance is None:
            self.view.camera.distance = 10.0
        if self.view.camera is self.turntableCamera:
            self.zoom_size = self.ori_distance / self.view.camera.distance
            # self.zoom_size += event.delta[1]
            self.zoom_text_visual.text = 'X %s' % round(self.zoom_size, 1)
            self.zoom_timer.start(interval=0.2, iterations=8)
        # TODO: add a bound for fly_mode mouse_wheel'''
