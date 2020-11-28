import OpenGL.GL as gl
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
import numpy as np

from .Techniques.opengl_camera import OglCamera
from GUI.Controls.Plot.Plottables import Rectangle
from PyQt5.QtWidgets import QOpenGLWidget

class PlotView(QtCore.QObject):
    signal_mouse_moved = QtCore.pyqtSignal(float, float)
    signal_mouse_clicked = QtCore.pyqtSignal(float, float, object)

    signal_plot_range_changed = QtCore.pyqtSignal(object)

    signal_rect_selected = QtCore.pyqtSignal(float, float, float, float)

    def __init__(self, t, l, b, r, image_axes=True):
        super(PlotView, self).__init__()

        self._parent = None

        # sets if the axes have the same scale, i.e. to preserve pixel square-ness in images
        self.equal_axes_scale = image_axes

        self.draw_limits = np.array([t, l, b, r])

        self.view_camera = OglCamera(invert_y=False)

        self.widgets = []

        self.selection_rect = Rectangle(visible=False,
                                        fill_colour=np.array([233, 142, 34, 100]) / 255,
                                        border_colour=np.array([233, 142, 34, 255]) / 255,
                                        border_width=1, z_value=999)

        #
        # Mouse moving stuffs
        #
        self.clicked_object = None

        self.mouse_down_pos = None
        self.mouse_last_pos = None
        self.mouse_is_dragging = None
        self.mouse_drag_modifiers = None

    @property
    def parent(self: QOpenGLWidget):
        return self._parent

    @parent.setter
    def parent(self, p: QOpenGLWidget):
        self._parent = p
        self.selection_rect.parent = p

    def initialise(self):
        for w in self.widgets:
            w.initialise()

        self.selection_rect.initialise()
        # self.selection_rect.set_data(0,0,0,0)

    @property
    def draw_range_x(self):
        return self.draw_limits[3] - self.draw_limits[1]

    @property
    def draw_range_y(self):
        return self.draw_limits[2] - self.draw_limits[0]

    def scene_limits(self):
        _limits = np.array([0, 0, 0, 0], dtype=np.float32)
        for technique in self.widgets:
            larger = technique.limits > _limits
            larger[1:3] = ~larger[1:3]  # becase we want these to be smaller
            _limits[larger] = technique.limits[larger]

        return _limits

    @property
    def z_value(self):
        return 999

    @property
    def visible(self):
        return True

    def fit_view(self, extend=1.0):  # , preserve_aspect=True):

        lims = self.scene_limits()

        w = lims[3] - lims[1]
        h = lims[0] - lims[2]

        if self.equal_axes_scale:
            # we have to correct for the shape of our window
            aspect = self.draw_range_x / self.draw_range_y

            # if preserve_aspect:
            if w / h > aspect:
                view_width = w * extend
                view_height = view_width / aspect
            else:
                view_height = h * extend
                view_width = view_height * aspect

            dw = (view_width - w) / 2
            dh = (view_height - h) / 2

            self.view_camera.set_projection_limits(lims[0] + dh, lims[1] - dw, lims[2] - dh, lims[3] + dw)
        else:
            self.view_camera.set_projection_limits(lims[0], lims[1], lims[2], lims[3])

        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def add_widget(self, widget, index=None, fit=False):
        widget.parent = self.parent

        # # todo move this into parent setters above
        # if self.parent.isValid():
        #     widget.initialise()

        if index is None:
            self.widgets.append(widget)
            self.widgets.sort(key=lambda x: x.z_value)  # this is important for rendering transparancy
        else:
            self.widgets.insert(index, widget)

        if fit:
            self.fit_view(extend=1.0)

    def remove_widget(self, item, fit=False):
        i = None
        if item in self.widgets:
            i = self.widgets.index(item)
            self.widgets.remove(item)

        if fit:
            self.fit_view(extend=1.01)

        return i

    def resize(self, width, height):
        if self.parent is not None:
            self.draw_limits = np.array([self.parent.top_border_position,
                                         self.parent.left_border_position,
                                         self.parent.bottom_border_position,
                                         self.parent.right_border_position])

        if self.equal_axes_scale:
            self.view_camera.set_width_height(self.draw_range_x, self.draw_range_y)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def render(self, _projection, _width, _height, _px_ratio):
        if self.view_camera.invert_y:
            gl.glFrontFace(gl.GL_CCW)

        # the arguments into this function will be the whole plot sizes, so we need to calculate our viewport sizes
        screen_id = QApplication.desktop().screenNumber(self.parent)
        screen = QApplication.desktop().screen(screen_id)
        pr = screen.devicePixelRatio()

        width = int(pr * self.draw_range_x)
        height = int(pr * self.draw_range_y)

        x0 = int(pr * self.draw_limits[1])
        y0 = int(pr * (self.parent.y_range - self.draw_limits[2])) # note the switch of origin for glviewport

        rw = self.view_camera.projection_edges[3] - self.view_camera.projection_edges[1]
        rh = self.view_camera.projection_edges[0] - self.view_camera.projection_edges[2]

        if rw == 0 or rh == 0:
            return

        ratio_x = width / rw
        ratio_y = height / rh

        ratio = (ratio_x, ratio_y)

        projection = self.view_camera.get_projection_matrix()

        gl.glViewport(x0, y0, int(_px_ratio[0] * width), int(_px_ratio[1] * height))

        for w in self.widgets:
            w.render(projection, width, height, ratio)

        self.selection_rect.render(projection, width, height, ratio)

        gl.glViewport(0, 0, _width, _height)
        gl.glFrontFace(gl.GL_CW) # set back to default

    # def propogate_click(self, pos_x, pos_y):
    #     print("prop")

    def emit_mouse_coordinates(self, pos_x, pos_y):
        p_x, p_y = self.parent_coords_to_view_position(pos_x, pos_y)
        self.signal_mouse_moved.emit(p_x, p_y)

    def on_mouse_press(self, pos_x, pos_y, button, modifiers):
        if not self.parent_coords_within_draw_limits(pos_x, pos_y):
            return None

        # this is all using the plot coordinates, not the view
        self.mouse_down_pos = (pos_x, pos_y)
        self.mouse_last_pos = (pos_x, pos_y)
        self.mouse_is_dragging = False
        self.mouse_drag_modifiers = modifiers

        self.clicked_object = None

        for widge in self.widgets:
            if self.clicked_object is None:
                p_x, p_y = self.parent_coords_to_view_position(pos_x, pos_y)
                grabber = widge.on_click(p_x, p_y, (1.0, 1.0))  # TODO: use this coord system???

                if grabber is not None:
                    self.clicked_object = grabber
            else:
                widge.selected = False

        self.selection_rect.set_data(0, 0, 0, 0)

        return self

    def on_mouse_move(self, pos_x, pos_y, button, modifiers):
        #
        # Star by testing if we are really dragging (i.e. not just jitter)
        # and get the movement we have made
        #

        dx = 0.0
        dy = 0.0

        if button == QtCore.Qt.LeftButton:
            dx = pos_x - self.mouse_last_pos[0]
            dy = pos_y - self.mouse_last_pos[1]

            do_x = abs(pos_x - self.mouse_down_pos[0])
            do_y = abs(pos_y - self.mouse_down_pos[1])

            move_minimum = 4
            if do_x >= move_minimum or do_y >= move_minimum:
                self.mouse_is_dragging = True

        self.mouse_last_pos = (pos_x, pos_y)

        if not self.mouse_is_dragging:
            return


        #
        # Propogate the mouse drag to any objects that may need it
        #

        if self.clicked_object is not None:
            p_x, p_y = self.parent_coords_to_view_position(pos_x, pos_y)
            if self.clicked_object.on_drag(p_x, p_y, modifiers):
                return

        #
        # Handle our selection box size/hide
        # or just pan if nothing else is going on
        #

        if modifiers & QtCore.Qt.ControlModifier \
                and self.mouse_drag_modifiers & QtCore.Qt.ControlModifier \
                and button & QtCore.Qt.LeftButton:
            start_pos = self.parent_coords_to_view_position(self.mouse_down_pos[0], self.mouse_down_pos[1])
            current_pos = self.parent_coords_to_view_position(pos_x, pos_y)

            # get t,l,b,r
            top = max(start_pos[1], current_pos[1])
            bottom = min(start_pos[1], current_pos[1])
            left = min(start_pos[0], current_pos[0])
            right = max(start_pos[0], current_pos[0])

            self.selection_rect.visible = True
            self.selection_rect.set_data(top, left, bottom, right)

        elif not modifiers & QtCore.Qt.ControlModifier \
                and self.mouse_drag_modifiers & QtCore.Qt.ControlModifier:
            self.selection_rect.visible = False

        elif not self.mouse_drag_modifiers & QtCore.Qt.ControlModifier \
                and button & QtCore.Qt.LeftButton:
            self.view_camera.mouse_pan(dx, dy, self.draw_range_x, self.draw_range_y)
            self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def on_mouse_release(self, pos_x, pos_y, button, modifiers):
        if button == QtCore.Qt.RightButton:
            self.fit_view(extend=1.0)

        if not self.mouse_is_dragging and button == QtCore.Qt.LeftButton:
            # pos_x, pos_y are the
            p_x, p_y = self.parent_coords_to_view_position(pos_x, pos_y)
            self.signal_mouse_clicked.emit(p_x, p_y, modifiers)

        if self.mouse_is_dragging and self.mouse_drag_modifiers & QtCore.Qt.ControlModifier and modifiers & QtCore.Qt.ControlModifier:
            start_pos = self.parent_coords_to_view_position(self.mouse_down_pos[0], self.mouse_down_pos[1])
            current_pos = self.parent_coords_to_view_position(pos_x, pos_y)

            # get t,l,b,r
            top = max(start_pos[1], current_pos[1])
            bottom = min(start_pos[1], current_pos[1])
            left = min(start_pos[0], current_pos[0])
            right = max(start_pos[0], current_pos[0])

            self.signal_rect_selected.emit(top, left, bottom, right)

        self.selection_rect.visible = False

    def on_mouse_scroll(self, pos_x, pos_y, delta):
        if not self.parent_coords_within_draw_limits(pos_x, pos_y):
            return None

        frac_x, frac_y = self.parent_coords_to_view_fraction(pos_x, pos_y)

        self.view_camera.mouse_scroll(delta, (frac_x, frac_y))
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def on_mouse_scroll_horizontal(self, delta, frac):
        self.view_camera.scroll_width(delta, frac)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def on_mouse_scroll_vertical(self, delta, frac):
        self.view_camera.scroll_height(delta, frac)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def on_mouse_pan_horizontal(self, delta):
        self.view_camera.mouse_pan(delta, 0, self.draw_range_x, self.draw_range_y)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def on_mouse_pan_vertical(self, delta):
        self.view_camera.mouse_pan(0, delta, self.draw_range_x, self.draw_range_y)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    # This keeps the origin the same and stretched the axes from there
    def on_mouse_stretch_horizontal(self, delta):
        self.view_camera.mouse_stretch_from_origin(delta, 0, self.draw_range_x, self.draw_range_y)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def on_mouse_stretch_vertical(self, delta):
        self.view_camera.mouse_stretch_from_origin(0, delta, self.draw_range_x, self.draw_range_y)
        self.signal_plot_range_changed.emit(self.view_camera.projection_edges)

    def parent_coords_within_draw_limits(self, pos_x, pos_y):
        frac_x, frac_y = self.parent_coords_to_view_fraction(pos_x, pos_y)
        return 0.0 <= frac_x <= 1.0 and 0.0 <= frac_y <= 1.0

    # this takes to coords from the parent widget (i.e. the overall plot) and convert them to positions within this
    def parent_coords_to_view_fraction(self, pos_x, pos_y):
        px = (pos_x - self.draw_limits[1]) / self.draw_range_x
        py = (pos_y - self.draw_limits[0]) / self.draw_range_y

        return px, py

    def parent_coords_to_view_position(self, pos_x, pos_y):  # TODO: combine this with the function below?
        fractional_pos_x, fractional_pos_y = self.parent_coords_to_view_fraction(pos_x, pos_y)

        pos = self.view_camera.mouse_position((fractional_pos_x, fractional_pos_y))
        return pos

    # TODO: used to be 'self.parent.widget_size_to_image' used in scatter plot?

    def screen_size_to_view(self, var):
        if isinstance(var, (QtCore.QPointF, QtCore.QPointF)):
            x = var.x()
            y = var.y()
        elif isinstance(var, tuple):
            x = var[0]
            y = var[1]
        else:
            x = var
            y = var

        fractional_pos_x = x / self.draw_range_x
        fractional_pos_y = y / self.draw_range_y

        pos = self.view_camera.mouse_position((fractional_pos_x, fractional_pos_y), False)
        return pos