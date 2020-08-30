from PyQt5 import QtCore
import numpy as np

from GUI.Controls.Plot.Techniques.opengl_circle_technique import OglCircleTechnique
from GUI.Controls.Plot.Techniques.opengl_scatter_technique import OglScatterTechnique
from .handle import Handle


class CircleAnnotation(QtCore.QObject):
    # pass the limits of the rectangle
    signal_changed = QtCore.pyqtSignal(float, float, float, float)

    def __init__(self, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2,
                 z_value=1, visible=True,
                 selectable=True, movable=True, resizable=True, maintain_aspect=False, resize_symmetric=False):
        super(CircleAnnotation, self).__init__()

        self.selected = False

        # these parameters are used for resizing symmetrically or keeping the same aspect ratio
        self.start_click_limits = None
        # this is used to calculate the mouse drag delta
        self.start_click_pos = None

        # these are used to control the 'interactivity'
        self.selectable_set = selectable  # stores if we want interact with this (doesnt account for visibility)
        self.selectable = selectable and visible  # TODO: should be a property
        self.movable = movable  # can we move this widget, or just resize it
        self.resizable = resizable  # sets if we can resize it, or just move it
        self.maintain_aspect = maintain_aspect  # forces the same aspect (i.e. holding shift)
        self.resize_symmetric = resize_symmetric  # forces the resizing about the centre point (i.e. holding control)

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        self.circle = OglCircleTechnique(fill_colour=fill_colour,
                                         border_colour=border_colour,
                                         border_width=border_width,
                                         z_value=z_value, visible=visible)

        self.circle.initialise()

        self.handle_size = 10
        self.handles = {}
        ids = ['tl', 'tr', 'br', 'bl']
        for i in ids:
            h = Handle(size=self.handle_size,
                       fill_colour=np.array([0., 1., 0., 1.0]),
                       border_width=0.,
                       id=i, z_value=z_value)

            h.signal_drag.connect(self.handle_drag)
            self.handles[i] = h

    @property
    def z_value(self):
        return self.circle.z_value

    def initialise(self):
        return

    def get_centre(self) -> tuple:
        lims = self.limits
        c_x = (lims[3] + lims[1]) / 2.0
        c_y = (lims[0] + lims[2]) / 2.0
        return c_y, c_x

    def get_limit_centre(self, lims) -> tuple:
        c_x = (lims[3] + lims[1]) / 2.0
        c_y = (lims[0] + lims[2]) / 2.0
        return c_y, c_x

    def get_radii(self):
        lims = self.limits
        r_x = abs(lims[3] - lims[1]) / 2.0
        r_y = abs(lims[0] - lims[2]) / 2.0

        return r_y, r_x

    def get_side_lengths(self, lims) -> tuple:
        r_x = (lims[3] - lims[1])
        r_y = (lims[0] - lims[2])
        return r_y, r_x

    def get_aspect_ratio(self, lims) -> float:
        ry, rx = self.get_side_lengths(lims)
        return rx / ry

    @QtCore.pyqtSlot(float, float, object)
    def handle_drag(self, px, py, modifiers, emit=True):
        if not self.resizable:
            return

        # todo: before we start moving stuff, get the offset between the mouse position and the handle centre?

        if self.resize_symmetric or modifiers & QtCore.Qt.ControlModifier:
            # get the original centre
            cy, cx = self.get_limit_centre(self.start_click_limits)

            # get the difference from the current point to the centre
            dx = px - cx
            dy = py - cy

            if self.sender() == self.handles['tr']:
                t = cy + dy
                l = cx - dx
                b = cy - dy
                r = cx + dx
            elif self.sender() == self.handles['tl']:
                t = cy + dy
                l = cx + dx
                b = cy - dy
                r = cx - dx
            elif self.sender() == self.handles['bl']:
                t = cy - dy
                l = cx + dx
                b = cy + dy
                r = cx - dx
            elif self.sender() == self.handles['br']:
                t = cy - dy
                l = cx - dx
                b = cy + dy
                r = cx + dx
            else:
                return
        else:
            # get my original limits
            t = self.start_click_limits[0]
            l = self.start_click_limits[1]
            b = self.start_click_limits[2]
            r = self.start_click_limits[3]

            # get which handle I'm adjusting
            if self.sender() == self.handles['tl']:
                t = py
                l = px
            elif self.sender() == self.handles['tr']:
                t = py
                r = px
            elif self.sender() == self.handles['br']:
                b = py
                r = px
            elif self.sender() == self.handles['bl']:
                b = py
                l = px
            else:
                return

        if self.maintain_aspect or modifiers & QtCore.Qt.ShiftModifier:
            new_height = t - b
            new_width = r - l
            new_aspect = abs(new_width) / abs(new_height)
            start_aspect = self.get_aspect_ratio(self.start_click_limits)

            if new_aspect < start_aspect:
                # print('new aspect is narrow')
                # new aspect is 'more tall' -> adjust the y value
                new_width = new_height * start_aspect
            elif new_aspect > start_aspect:
                # print('new aspect is wide')
                new_height = new_width / start_aspect

            # if control modifier, just apply this correction to either side equally
            if self.resize_symmetric or modifiers & QtCore.Qt.ControlModifier:
                cx = (r + l) / 2
                cy = (t + b) / 2
                t = cy + new_height / 2
                l = cx - new_width / 2
                b = cy - new_height / 2
                r = cx + new_width / 2
            else:
                # get which handle I'm adjusting
                if self.sender() == self.handles['tl']:
                    t = b + new_height
                    l = r - new_width
                elif self.sender() == self.handles['tr']:
                    t = b + new_height
                    r = l + new_width
                elif self.sender() == self.handles['br']:
                    b = t - new_height
                    r = l + new_width
                elif self.sender() == self.handles['bl']:
                    b = t - new_height
                    l = r - new_width
                else:
                    return

        # this handles when we drag a handle to the other side of another
        # e.g. the top left becomes the bottom left
        if t < b:
            self.handles['tl'], self.handles['bl'] = self.handles['bl'], self.handles['tl']
            self.handles['tr'], self.handles['br'] = self.handles['br'], self.handles['tr']
            self.start_click_limits[0], self.start_click_limits[2] = self.start_click_limits[2], self.start_click_limits[0]

        if r < l:
            self.handles['tl'], self.handles['tr'] = self.handles['tr'], self.handles['tl']
            self.handles['bl'], self.handles['br'] = self.handles['br'], self.handles['bl']
            self.start_click_limits[1], self.start_click_limits[3] = self.start_click_limits[3], self.start_click_limits[1]

        c_x = (r + l) / 2
        c_y = (t + b) / 2

        r_x = abs(r - l) / 2
        r_y = abs(t - b) / 2

        self.make_buffers_circle(c_x, c_y, r_x, r_y, emit)
        # self.make_buffers_rect(t, l, b, r)

    # this includes things that are constant size on screen!
    def get_limits(self, ratio):
        # todo: implement handle class version of this, then just do a max/min search
        return self.limits + np.array([1., -1., -1., 1.]) * self.handle_size / (2 * ratio)

    def on_drag(self, px, py, modifiers):
        if not self.movable:
            return False

        c_y, c_x = self.get_limit_centre(self.start_click_limits)

        # todo: modify these if shift is pressed
        # i think just detect which is bigger (vertical or horizontal) and set the other to zero
        # could also do 45 degrees, do this based on the ration of horizontal to vertical
        c_x += px - self.start_click_pos[0]
        c_y += py - self.start_click_pos[1]

        l_x, l_y = self.get_side_lengths(self.start_click_limits)

        self.make_buffers_circle(c_x, c_y, l_x / 2, l_y / 2)

        return True

    def on_click(self, pos_x, pos_y, ratio):
        lim = self.get_limits(ratio[0])
        # this is a coarse hit detection (is it in the rect we have)
        if not self.selectable or lim[1] > pos_x or pos_x > lim[3] or lim[2] > pos_y or pos_y > lim[0]:
            self.selected = False
            return None

        # now detect if we have hit the handles
        for handle in self.handles.values():
            hit = handle.on_click(pos_x, pos_y, ratio)
            if hit is not None:
                self.start_click_limits = np.copy(self.limits)
                self.start_click_pos = (pos_x, pos_y)  # is this needed?
                return handle

        # now detect if we have hit the actually annotation
        d_x = pos_x - (self.limits[3] + self.limits[1]) / 2
        d_y = pos_y - (self.limits[0] + self.limits[2]) / 2

        r_x = d_x / (0.5 * (self.limits[3] - self.limits[1]))
        r_y = d_y / (0.5 * (self.limits[0] - self.limits[2]))
        r = r_x**2 + r_y**2

        if r <= 1.0:
            self.selected = True
            self.start_click_limits = np.copy(self.limits)
            self.start_click_pos = (pos_x, pos_y)
            return self
        else:  # TODO: this may want to be controlled externally?
            self.selected = False  # todo: could make it stay selected until something else is selected?

        return None

    def make_buffers(self, centre_x, centre_y, radius_x, radius_y):
        self.make_buffers_circle(centre_x, centre_y, radius_x, radius_y)

    def make_buffers_circle(self, centre_x, centre_y, radius_x, radius_y, emit=True):
        t = centre_y + radius_y
        l = centre_x - radius_x
        b = centre_y - radius_y
        r = centre_x + radius_x

        self.handles['tl'].set_position(l, t)
        self.handles['tr'].set_position(r, t)
        self.handles['br'].set_position(r, b)
        self.handles['bl'].set_position(l, b)

        c_x = (r + l) / 2.0
        c_y = (t + b) / 2.0

        r_x = (r - l) / 2.0
        r_y = (t - b) / 2.0

        self.circle.make_buffers(c_x, c_y, r_x, r_y)

        # accounting for size of handles is done later
        self.limits[0] = max(t, b)
        self.limits[1] = min(l, r)
        self.limits[2] = min(t, b)
        self.limits[3] = max(l, r)

        if emit:
            self.signal_changed.emit(t, l, b, r)

    def set_radius(self, r_x, r_y=None, emit=True):
        if r_y is None:
            r_y = r_x

        c_y, c_x = self.get_centre()

        self.make_buffers_circle(c_x, c_y, r_x, r_y, emit)

    def set_position(self, c_x, c_y):
        r_y, r_x = self.get_radii()

        self.make_buffers_circle(c_x, c_y, r_x, r_y)

    def set_position_radius(self, c_x, c_y, r_x, r_y):
        self.make_buffers_circle(c_x, c_y, r_x, r_y)

    def render(self, projection, width, height, ratio):
        self.circle.render(projection, width, height, ratio)

        if self.selected:
            for handle in self.handles.values():
                handle.render(projection, width, height, ratio)

    def set_visible(self, is_visible):
        if not is_visible:
            self.selected = False  # should take care of handles?
        self.selectable = self.selectable_set and is_visible
        self.circle.visible = is_visible
