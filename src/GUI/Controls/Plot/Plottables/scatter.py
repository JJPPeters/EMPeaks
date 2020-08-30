from PyQt5 import QtGui, QtCore
import numpy as np

# from .plotwidget import PlotWidget
from GUI.Controls.Plot.Techniques import OglScatterTechnique

from Processing.Utilities import point_array_in_rect
from Processing.Utilities import get_point_distance
from GUI.Utilities.enums import AnnotationType


class ScatterPlot(OglScatterTechnique, QtCore.QObject):
    def __init__(self, points=None, points_y=None, size=1, fill_colour=np.zeros((4,)),
                 border_width=1, border_colour=np.ones((4, )),
                 selected_fill_colour=None, selected_border_colour=None, use_screen_space=True,
                 z_value=1, visible=True):
        super(ScatterPlot, self).__init__(size_x=size, fill_colour=fill_colour, border_width=border_width, border_colour=border_colour, selected_fill_colour=selected_fill_colour, selected_border_colour=selected_border_colour, use_screen_space=use_screen_space, z_value=z_value, visible=visible)

        self.plot_type = AnnotationType.Scatter

        self.basis = None

        self._parent = None

        self.selected_peaks = None
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

            x = x.reshape(1, -1)
            y = y.reshape(1, -1)

            x = np.hstack(x, y)
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
        self.selected_peaks = None
        self.append_points(np.array([py, px]).reshape(1, -1))

    def select_from_click(self, px, py):
        # This scatter size in defined in SCREEN UNITS (at least on non-scaled displays)
        # scatter size is also the DIAMETER
        screen_size = self.radii[0]

        # convert this to image units
        image_size = self.parent.plot_view.screen_size_to_view(screen_size)
        r = image_size[0] / 2

        self.select_in_circle(px, py, r)

    def select_in_rectangle(self, top, left, bottom, right):
        if self.parent is None:
            return
        self.parent.makeCurrent()

        # get a list of points inside the region
        self.selected_peaks = point_array_in_rect(self.points, top, left, bottom, right)

        # update what we need? (use np.where to get indices
        self.selected_buffer.update_all(self.selected_peaks.astype(np.int32))

        if self.parent is not None:
            self.parent.update()

    def select_in_circle(self, centre_x, centre_y, radius):
        if self.parent is None:
            return
        self.parent.makeCurrent()

        # get a list of points inside a rect to quickly cut down our options
        # this returns a boolean array
        selected_peaks = point_array_in_rect(self.points,
                                             centre_y + radius,
                                             centre_x - radius,
                                             centre_y - radius,
                                             centre_x + radius)

        for peak_index in np.where(selected_peaks)[0]:
            peak_pos = self.points[peak_index, :]
            if get_point_distance(peak_pos[1], peak_pos[0], centre_x, centre_y) > radius:
                selected_peaks[peak_index] = False

        self.selected_peaks = selected_peaks

        # update what we need only??
        self.selected_buffer.update_all(self.selected_peaks.astype(np.int32))

        if self.parent is not None:
            self.parent.update()

    def delete_selected(self):
        if self.selected_peaks is None or self.selected_peaks.size == 0:
            return

        self.points = self.points[np.logical_not(self.selected_peaks), :]
        self.selected_peaks = None

        # TODO: handle if all peaks are to be deleted
        if self.points.size == 0:
            return

        self.make_buffers(self.points)

        if self.parent is not None:
            self.parent.update()
