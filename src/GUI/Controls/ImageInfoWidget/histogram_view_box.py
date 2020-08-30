from PyQt5 import QtCore, QtGui
from GUI.Controls.Plot import PlotWidget
import numpy as np


class HistogramViewBox(PlotWidget):

    sigLimitsChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwds):
        super(HistogramViewBox, self).__init__(*args, **kwds)

        # self.plot_view.view_camera.invert_y = True

        self.setInvertY(True)

        self.mouse_down_pos = None
        self.mouse_is_dragging = False

        self.plot_view.selection_rect.fill_colour = np.array([255, 255, 255, 100], dtype=np.float32) / 255
        self.plot_view.selection_rect.border_colour = np.array([255, 255, 255, 255], dtype=np.float32) / 255

        # need to start off with the default so we can rewind to it
        self.axHistory = []

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            return

        pos_x = ev.pos().x()
        self.mouse_down_pos = pos_x
        self.mouse_is_dragging = False

        self.update()

    def mouseMoveEvent(self, ev):
        dx = 0.0

        if ev.buttons() == QtCore.Qt.LeftButton:
            dx = ev.pos().x() - self.mouse_down_pos
            do_x = abs(dx)
            move_minimum = 4
            if do_x >= move_minimum:
                self.mouse_is_dragging = True

        if not self.mouse_is_dragging:
            self.plot_view.selection_rect.visible = False
            return

        self.makeCurrent()

        # draw our selection rect
        self.plot_view.selection_rect.visible = True

        left = np.min([self.mouse_down_pos, ev.pos().x()]) / self.width()
        right = np.max([self.mouse_down_pos, ev.pos().x()]) / self.width()

        self.plot_view.selection_rect.update_buffers(10, left, -10, right)
        self.update()

    def wheelEvent(self, event):
        return

    def mouseReleaseEvent(self, ev):
        self.mouse_is_dragging = False
        self.plot_view.selection_rect.visible = False

        if ev.button() == QtCore.Qt.RightButton:
            self.stepBackHistory()
            return

        sel_lim = self.plot_view.selection_rect.limits
        left = sel_lim[1]
        right = sel_lim[3]

        self.axHistory.append((left, right))
        self.sigLimitsChanged.emit()

    def updateScaleBox(self, p1, p2):
        r = QtCore.QRectF(p1, p2)
        self.clipRect(r)
        r = self.childGroup.mapRectFromParent(r)
        self.rbScaleBox.setPos(r.topLeft())
        self.rbScaleBox.resetTransform()
        self.rbScaleBox.scale(r.width(), r.height())
        self.rbScaleBox.show()

    def clipRect(self, r):
        vbRect = self.boundingRect()
        r.setTop(vbRect.top())
        r.setBottom(vbRect.bottom())

        if r.left() < vbRect.left():
            r.setLeft(vbRect.left())

        if r.right() > vbRect.right():
            r.setRight(vbRect.right())

    def stepBackHistory(self):
        if len(self.axHistory) < 2:
            return

        self.axHistory = self.axHistory[:-1]
        self.sigLimitsChanged.emit()

    def rewindHistory(self):
        self.axHistory = self.axHistory[:1]
        self.sigLimitsChanged.emit()
