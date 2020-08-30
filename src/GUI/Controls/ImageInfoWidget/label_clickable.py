from PyQt5 import QtCore, QtGui, QtWidgets


class QLabelClickable(QtWidgets.QLabel):

    sigDoubleClick = QtCore.pyqtSignal()

    def __init__(self, *args, **kargs):
        super(QLabelClickable, self).__init__(*args, **kargs)

    def mouseDoubleClickEvent(self, ev):
        self.sigDoubleClick.emit()
