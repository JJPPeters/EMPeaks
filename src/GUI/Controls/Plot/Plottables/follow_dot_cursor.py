from PyQt5 import QtCore
import scipy.spatial as spatial
import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget

from GUI.Controls.Plot.Techniques import OglScatterTechnique


class FollowDotCursor(QtCore.QObject):
    def __init__(self, view):

        super(FollowDotCursor, self).__init__()

        self._parent = None

        self.x = 0
        self.y = 0

        self._view = view
        self._points = None
        self.tree = None

        # can make the cursor options user set maybe?
        self.cursor = None

    @property
    def parent(self: QOpenGLWidget):
        return self._parent

    @parent.setter
    def parent(self, p: QOpenGLWidget):
        self._parent = p
        if self.cursor is not None:
            self.cursor.parent = p

    def on_click(self, pos_x, pos_y, ratio):
        return None

    def render(self, projection, width, height, ratio):
        if self.cursor is not None:
            self.cursor.render(projection, width, height, ratio)

    def select_from_points(self, points):
        if self.parent is not None:
            self.parent.makeCurrent()

        self._points = points
        self.tree = spatial.cKDTree(self._points)

        self.cursor = OglScatterTechnique(size_x=15, border_width=0,
                                          fill_colour=np.array([0, 0, 255, 120]) / 255,
                                          z_value=999, visible=False)
        self.cursor.make_buffers(np.array([0, 0], dtype=np.float32).reshape((-1, 2)))
        self.cursor.parent = self._parent

        self.start_cursor()

    def start_cursor(self):
        self._view.plot_view.signal_mouse_moved.connect(self.on_move)

    def update_points(self, points):
        self._points = points
        self.tree = spatial.cKDTree(self._points)

    def on_move(self, pos_x, pos_y):
        self.snap_point(pos_x, pos_y)

    def snap_point(self, pos_x, pos_y):
        # if self._view.scene_contains(pos_x, pos_y):
        self.y, self.x = self._snap(pos_y, pos_x)
        p = np.array([self.y, self.x], dtype=np.float32)
        self.cursor.visible = True
        if self.parent is not None:
            self.parent.makeCurrent()
        self.cursor.position_buffer.update_all(p.reshape((-1, 2)))  # This 0.5 is to put the cursor in the middle of the pixels
        self._view.update()

    def _snap(self, y, x):
        _, idx = self.tree.query((y, x), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            return 0, 0

    def stop_cursor(self):
        # clear the plot
        self._view.update()

        self._view.plot_view.signal_mouse_moved.disconnect(self.on_move)

