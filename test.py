from OpenGL import GL
from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtOpenGL import QGLWidget

class MyGL(QGLWidget):
    def paintGL(self):
        print('paint')
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glColor3f(0.0,0.0,1.0)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(0.1, 0.3)
        GL.glVertex2f(0.2, 0.4)
        GL.glEnd()

    def initializeGL(self):
        print('initialize')
        GL.glClearColor(0.50, 0.50, 0.50, 1.0) # Grey
        GL.glClearDepth(1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)

app = QApplication([''])
w = MyGL()
w.show()
app.processEvents()
