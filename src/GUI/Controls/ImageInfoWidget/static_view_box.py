from GUI.Controls.Plot import PlotWidget


class StaticViewBox(PlotWidget):

    def __init__(self, *args, **kwds):
        super(StaticViewBox, self).__init__(*args, **kwds)

    def keyPressEvent(self, ev):
        ev.ignore()

    def wheelEvent(self, ev, axis=None):
        ev.ignore()

    def mousePressEvent(self, ev):
        ev.ignore()

    def mouseMoveEvent(self, ev):
        ev.ignore()

    def mouseReleaseEvent(self, ev):
        ev.ignore()
