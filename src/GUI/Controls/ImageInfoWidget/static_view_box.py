from PyQt5 import QtCore
import numpy as np

from GUI.Controls.Plot import PlotWidget
from GUI.Controls.Plot.Plottables import Circle


class StaticViewBox(PlotWidget):

    sigLimitsChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwds):
        super(StaticViewBox, self).__init__(*args, **kwds)

        self.selection_circ = Circle(centre=[0.0, 0.0], radii=[0.0, 0.0], visible=False,
                                     fill_colour=np.array([233, 142, 34, 100]) / 255,
                                     border_colour=np.array([233, 142, 34, 255]) / 255,
                                     border_width=2, z_value=999)

        self.selection_circ.fill_colour = np.array([255, 255, 255, 100], dtype=np.float32) / 255
        self.selection_circ.border_colour = np.array([255, 255, 255, 255], dtype=np.float32) / 255

        self.plot_view.add_widget(self.selection_circ)

        self.mouse_down_radius = None
        self.mouse_down_px = None
        self.mouse_is_dragging = False
        # need to start off with the default so we can rewind to it
        self.axHistory = []

    def keyPressEvent(self, ev):
        ev.ignore()

    def wheelEvent(self, ev, axis=None):
        ev.ignore()

    def position_to_radius(self, pos):
        p_plot = self.plot_view.parent_coords_to_view_position(pos.x(), pos.y())
        return np.sqrt(p_plot[0]**2 + p_plot[1]**2)

    def mousePressEvent(self, ev):
        r = self.position_to_radius(ev.pos())
        self.mouse_down_radius =r
        self.mouse_down_px = ev.pos()
        self.mouse_is_dragging = False

        self.update()

    def mouseMoveEvent(self, ev):
        epr = self.position_to_radius(ev.pos())
        if ev.buttons() == QtCore.Qt.LeftButton:
            dpos = ev.pos() - self.mouse_down_px
            d_px = np.sqrt(dpos.x()**2 + dpos.y()**2)
            move_minimum = 4
            if d_px >= move_minimum:
                self.mouse_is_dragging = True

        if not self.mouse_is_dragging:
            self.selection_circ.visible = False
            return

        self.makeCurrent()

        # draw our selection rect
        self.selection_circ.visible = True

        inner_r = np.min([self.mouse_down_radius, epr])
        outer_r = np.max([self.mouse_down_radius, epr])

        inner_r = np.clip(inner_r, 0.0, 1.0)
        outer_r = np.clip(outer_r, 0.0, 1.0)

        self.selection_circ.set_data(0.0, 0.0, outer_r, outer_r)
        self.selection_circ.ring_frac = inner_r / outer_r
        self.update()

    def mouseReleaseEvent(self, ev):
        self.mouse_is_dragging = False
        self.selection_circ.visible = False

        if ev.button() == QtCore.Qt.RightButton:
            self.stepBackHistory()
            return

        sel_lim = self.selection_circ.radii[0]  # assume they are the same (they hsould be!)
        left = sel_lim * self.selection_circ.ring_frac
        right = sel_lim

        self.axHistory.append((left, right))
        self.sigLimitsChanged.emit()

        self.update()

    def stepBackHistory(self):
        if len(self.axHistory) < 2:
            return

        self.axHistory = self.axHistory[:-1]
        self.sigLimitsChanged.emit()