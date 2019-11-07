import ctypes

from vispy import scene
canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)

from vispy.gloo import gl
from vispy.gloo.gl.gl2 import _get_gl_func 
print('OPENGL VERSION:', repr(gl.glGetParameter(gl.GL_VERSION)))

nativefunc = _get_gl_func("glGetString", ctypes.c_char_p, (ctypes.c_uint,))
res = nativefunc(gl.GL_VERSION)
print(repr(res))
print(repr(ctypes.string_at(res).decode('utf-8')))

