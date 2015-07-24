# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2015, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
# vispy: gallery 2

"""
Example volume rendering

Controls:

* 1  - toggle camera between first person (fly), regular 3D (turntable) and
       arcball
* 2  - toggle between volume rendering methods
* 3  - makes the data cube visible or not
* 4  - toggle between colormaps, depends on which rendering method is available
* 0  - reset cameras
* [] - decrease/increase isosurface threshold

With fly camera:

* WASD or arrow keys - move around
* SPACE - brake
* FC - move up-down
* IJKL or mouse - look around
"""

from itertools import cycle

import numpy as np

from vispy import app, scene, io
from vispy.color import get_colormaps, BaseColormap
import pyfits
# Read volume

fitsdata = pyfits.open('/Users/penny/PycharmProjects/untitled/l1448_13co.fits')
# fitsdata = pyfits.open('/Users/penny/Documents/CO/G25.4CO.fits')
#filename = input('Please input fits file name: ')
#if filename is not None:
#    fitsdata = pyfits.open(filename)
#else:
#    quit
naxis = fitsdata[0].header['NAXIS']
image = fitsdata[0].data
print naxis
if naxis < 3:
    print 'The data should not be less than 3 dimensions !'
    quit
elif naxis > 3:
    image = fitsdata[0].data[0,:,:,:]
print image.shape
# Set all nan to zero for display
vol1 = np.nan_to_num(np.array(image))

# Prepare canvas
canvas = scene.SceneCanvas(keys='interactive', size=(800, 600), show=True)
canvas.measure_fps()

# Set up a viewbox to display the image with interactive pan/zoom
view = canvas.central_widget.add_view()

# Set whether we are emulating a 3D texture
emulate_texture = False

# Create the volume visuals, only one is visible
volume1 = scene.visuals.Volume(vol1, parent=view.scene, threshold=0.1,
                               emulate_texture=emulate_texture)
# volume1.transform = scene.STTransform(translate=(64, 64, 0))

# Create two cameras (1 for firstperson, 3 for 3d person)
fov = 60.
cam1 = scene.cameras.FlyCamera(parent=view.scene, fov=fov, name='Fly')
cam2 = scene.cameras.TurntableCamera(parent=view.scene, fov=fov,
                                     name='Turntable')
cam3 = scene.cameras.ArcballCamera(parent=view.scene, fov=fov, name='Arcball')
view.camera = cam2  # Select turntable at first

fitsdata.close()

# create colormaps that work well for translucent and additive volume rendering
class TransFire(BaseColormap):
    glsl_map = """
    vec4 translucent_fire(float t) {
        return vec4(pow(t, 0.5), t, t*t, max(0, t*1.05 - 0.05));
    }
    """


class TransGrays(BaseColormap):
    glsl_map = """
    vec4 translucent_grays(float t) {
        return vec4(t, t, t, t*0.05);
    }
    """

# Setup colormap iterators
opaque_cmaps = cycle(get_colormaps())
translucent_cmaps = cycle([TransFire(), TransGrays()])
opaque_cmap = next(opaque_cmaps)
translucent_cmap = next(translucent_cmaps)
result = 1

# Implement key presses
@canvas.events.key_press.connect
def on_key_press(event):
    # result =1 # invoke every press...
    global opaque_cmap, translucent_cmap, result
    if event.text == '1':
        cam_toggle = {cam1: cam2, cam2: cam3, cam3: cam1}
        view.camera = cam_toggle.get(view.camera, cam2)
        print(view.camera.name + ' camera')
    elif event.text == '2':
        methods = ['mip', 'translucent', 'iso', 'additive']
        method = methods[(methods.index(volume1.method) + 1) % 4]
        print("Volume render method: %s" % method)
        cmap = opaque_cmap if method in ['mip', 'iso'] else translucent_cmap
        volume1.method = method
        volume1.cmap = cmap
    elif event.text == '3':
        volume1.visible = not volume1.visible
    elif event.text == '4':
        if volume1.method in ['mip', 'iso']:
            cmap = opaque_cmap = next(opaque_cmaps)
        else:
            cmap = translucent_cmap = next(translucent_cmaps)
        volume1.cmap = cmap

    elif event.text == '0':
        cam1.set_range()
        cam3.set_range()
    elif event.text != '' and event.text in '[]':
        s = -0.025 if event.text == '[' else 0.025
        volume1.threshold += s
        th = volume1.threshold if volume1.visible else volume2.threshold
        print("Isosurface threshold: %0.3f" % th)
#Add zoom out functionality for the third dimension
    elif event.text != '' and event.text in '=-':
        z = -1 if event.text == '-' else +1
        result += z
        if result > 0:
            volume1.transform = scene.STTransform(scale=(1, 1, result))
        else:
            result = 1
        print("Volume scale: %d" % result)

# for testing performance
#@canvas.connect
#def on_draw(ev):
    #canvas.update()

if __name__ == '__main__':
    print(__doc__)
    app.run()
