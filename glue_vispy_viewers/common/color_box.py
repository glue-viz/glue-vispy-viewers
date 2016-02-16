from glue.external.echo import add_callback
from glue.external.qt import QtCore, QtGui, get_qapp
from glue.utils.qt import mpl_to_qt4_color, qt4_to_mpl_color
from glue.utils import nonpartial

__all__ = ['QColorBox', 'connect_color']


def connect_color(client, prop, widget):

    def update_widget(text):
        widget.setColor(text)

    def update_prop():
        setattr(client, prop, widget.color())

    add_callback(client, prop, update_widget)
    widget.colorChanged.connect(update_prop)


class QColorBox(QtGui.QLabel):

    mousePressed = QtCore.Signal()
    colorChanged = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(QColorBox, self).__init__(*args, **kwargs)
        self.mousePressed.connect(nonpartial(self.query_color))
        self.colorChanged.connect(nonpartial(self.on_color_change))
        self.setColor("#000000")

    def mousePressEvent(self, event):
        self.mousePressed.emit()
        event.accept()

    def query_color(self):
        color = QtGui.QColorDialog.getColor(self._qcolor, self)
        if color.isValid():
            self.setColor(qt4_to_mpl_color(color))

    def setColor(self, color):
        self._color = color
        self.colorChanged.emit()

    def color(self):
        return self._color

    def on_color_change(self):
        self._qcolor = mpl_to_qt4_color(self.color())
        image = QtGui.QImage(self.width(), self.height(), QtGui.QImage.Format_RGB32)
        image.fill(self._qcolor)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.setPixmap(pixmap)


if __name__ == "__main__":

    app = get_qapp()

    label = QColorBox()
    label.resize(100,100)
    label.show()
    label.raise_()
    app.exec_()
