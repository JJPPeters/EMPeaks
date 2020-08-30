from PyQt5 import QtCore
import numpy as np

from GUI.Controls.Plot.Techniques.opengl_scatter_technique import OglScatterTechnique


class Handle(OglScatterTechnique, QtCore.QObject):
    signal_drag = QtCore.pyqtSignal(float, float, object)

    def __init__(self, position=None, size=1, fill_colour=np.zeros((4,)),
                 border_width=1, border_colour=np.ones((4, )),
                 selected_fill_colour=None, selected_border_colour=None, z_value=1, visible=True, id=None):
        OglScatterTechnique.__init__(self, size_x=size, fill_colour=fill_colour, border_width=border_width, border_colour=border_colour, selected_fill_colour=selected_fill_colour, selected_border_colour=selected_border_colour, z_value=z_value, visible=visible)
        QtCore.QObject.__init__(self)

        self.parent = None

        self.selected_peaks = None
        self.position = position

        self.initialise()

    def on_drag(self, pos_x, pos_y, modifiers):
        self.signal_drag.emit(pos_x, pos_y, modifiers)
        return True

    def get_limits(self, ratio):
        r_x = self.radii[0]
        r_y = self.radii[1]
        return self.limits + np.array([r_y, -r_x, -r_y, r_x]) / (2 * ratio[0])

    def on_click(self, pos_x, pos_y, ratios):
        h_lim = self.get_limits(ratios)

        if h_lim[1] > pos_x or pos_x > h_lim[3] or h_lim[2] > pos_y or pos_y > h_lim[0]:
            return None

        d_x = pos_x - (h_lim[3] + h_lim[1]) / 2
        d_y = pos_y - (h_lim[0] + h_lim[2]) / 2
        r = d_x ** 2 + d_y ** 2

        r_x = self.radii[0]
        r_y = self.radii[1]

        # TODO: make this function work for screen space and image space coordinates!
        # TODO: make this work for ovals

        if r <= (r_x / (2 * ratios[0])) ** 2:
            return self

    def set_position(self, x, y):
        self.position = np.array([y, x], dtype=np.float64)
        self.make_buffers(np.array([[y, x]]))
