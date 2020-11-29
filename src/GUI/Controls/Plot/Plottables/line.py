from PyQt5 import QtGui, QtCore
import numpy as np

from GUI.Controls.Plot.Techniques import OglLineTechnique

from PyQt5.QtWidgets import QOpenGLWidget

from GUI.Utilities.enums import AnnotationType


class LinePlot(OglLineTechnique, QtCore.QObject):
    def __init__(self, points=None, points_y=None, thickness=1, colour=None, z_value=1, visible=True):
        super(LinePlot, self).__init__(thickness=thickness, colour=colour / 255, z_value=z_value, visible=visible)

        self.plot_type = AnnotationType.Line

        self.points = None

        if points is not None:
            self.set_points(points, points_y)

    def set_points(self, x, y=None):
        if y is None:
            if x.ndim != 2 or x.shape[0] < 1 or x.shape[1] != 2:
                raise Exception("Trying to plot points with incorrect dimensions")
        else:
            # TODO: could handle python lists too
            if x.size != y.size:
                raise Exception("Trying to plot points with incorrect dimensions")

            x = x.reshape(-1, 1)
            y = y.reshape(-1, 1)

            x = np.hstack((y, x))
            y = None  # is this needed, really?

        self.points = x
        self.make_buffers(self.points)

    def append_points(self, points):
        if self.points is None or self.points.size == 0:
            self.points = points
        else:
            self.points = np.vstack((self.points, points))

        # update the buffers of the actual object
        self.make_buffers(self.points)

    def add_point(self, px, py):
        self.append_points(np.array([py, px]).reshape(1, -1))