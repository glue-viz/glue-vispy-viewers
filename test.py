from vispy import scene
canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)

from vispy.gloo import gl
print(gl.glGetParameter(gl.GL_VERSION))
