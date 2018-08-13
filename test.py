from PyQt5 import QtWebEngineWidgets
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtOpenGL import QGLWidget

app = QApplication([''])
w = QGLWidget()
w.show()
app.processEvents()

