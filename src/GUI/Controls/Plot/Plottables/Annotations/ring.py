from PyQt5 import QtCore
import numpy as np

from GUI.Controls.Plot.Techniques.opengl_circle_technique import OglCircleTechnique
from GUI.Controls.Plot.Techniques.opengl_scatter_technique import OglScatterTechnique
from .circle import CircleAnnotation
from .handle import Handle


class RingAnnotation(CircleAnnotation):
    signal_ring_changed = QtCore.pyqtSignal(float, float, float, float, float)

    def __init__(self, fill_colour=np.zeros((4,)), border_colour=np.ones((4,)), border_width=2, z_value=1, visible=True,
                 selectable=True, movable=True, resizable=True, maintain_aspect=False, resize_symmetric=False):
        super(RingAnnotation, self).__init__(fill_colour, border_colour, border_width, z_value, visible, selectable,
                                             movable, resizable, maintain_aspect, resize_symmetric)

        ids = ['in_tl', 'in_tr', 'in_br', 'in_bl']
        for i in ids:
            h = Handle(size=self.handle_size,
                       fill_colour=np.array([0., 1., 0., 1.0]),
                       border_width=0.,
                       id=i, z_value=z_value)

            h.signal_drag.connect(self.handle_drag)
            self.handles[i] = h

        self.signal_changed.connect(self.propogate_signal)

    def propogate_signal(self, p1, p2, p3, p4):
        lims = self.limits
        self.signal_ring_changed.emit(lims[0], lims[1], lims[2], lims[3], self.circle.ring_frac)
        # self.signal_ring_changed.emit(p1, p2, p3, p4, self.circle.ring_frac)

    def handle_drag(self, px, py, modifiers):
        # this is where most of the fun comes in!!!!
        # have to handle dragging the handles across each other (top to bottom, left to right) AS WELL as dragging inner
        # to outer...

        if not self.resizable:
            return

        # we need to update the inner radius fraction to be the same on screen dimension, so get the 'old' size
        old_full_width = self.limits[3] - self.limits[1]
        # old_full_height = limits[0] - limits[2]

        # this redraws the main circle and the outer handles
        # the false here is to stop the signal (that will e.g. update the textboxes is a band pass filter)
        # this will be done later after the inside fraction has been recalculated
        super(RingAnnotation, self).handle_drag(px, py, modifiers, False)

        # Now get the new size (so we can update the inner ring!)
        new_full_width = self.limits[3] - self.limits[1]
        # new_full_height = limits[0] - limits[2]

        # this will get modified later, but this adjusts the inner ring if the outer one has been changed
        # (we won't reach that part of the code if the handle being moved is an inner one
        self.circle.ring_frac *= old_full_width / new_full_width

        #
        # WARNING: If the outer radii has been adjusted, the next section of code will not run (well, some of it will)
        # because the next code test if the sending object was an 'inside' handle will exit
        # therefore, the signal to say 'things have been updated' is called in that if statement.
        # Just so you remember, future Jon.
        #

        # swap the inner and outer if we need to
        # (only need to check one coord)
        if self.handles['tl'].position[0] < self.handles['in_tl'].position[0]:
            self.handles['tl'], self.handles['in_tl'] = self.handles['in_tl'], self.handles['tl']
            self.handles['bl'], self.handles['in_bl'] = self.handles['in_bl'], self.handles['bl']
            self.handles['tr'], self.handles['in_tr'] = self.handles['in_tr'], self.handles['tr']
            self.handles['br'], self.handles['in_br'] = self.handles['in_br'], self.handles['br']

        #
        # These inside parts must always resize symmetrically and always maintain the aspect ratio
        #
        # get the original centre
        cy, cx = self.get_limit_centre(self.start_click_limits)

        # get the difference from the current point to the centre
        dx = px - cx
        dy = py - cy

        if self.sender() == self.handles['in_tr']:
            t = cy + dy
            l = cx - dx
            b = cy - dy
            r = cx + dx
        elif self.sender() == self.handles['in_tl']:
            t = cy + dy
            l = cx + dx
            b = cy - dy
            r = cx - dx
        elif self.sender() == self.handles['in_bl']:
            t = cy - dy
            l = cx + dx
            b = cy + dy
            r = cx - dx
        elif self.sender() == self.handles['in_br']:
            t = cy - dy
            l = cx - dx
            b = cy + dy
            r = cx + dx
        else:
            lims = self.limits
            self.signal_ring_changed.emit(lims[0], lims[1], lims[2], lims[3], self.circle.ring_frac)
            return

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
            if self.sender() == self.handles['in_tl']:
                t = b + new_height
                l = r - new_width
            elif self.sender() == self.handles['in_tr']:
                t = b + new_height
                r = l + new_width
            elif self.sender() == self.handles['in_br']:
                b = t - new_height
                r = l + new_width
            elif self.sender() == self.handles['in_bl']:
                b = t - new_height
                l = r - new_width
            else:
                return

        # this handles when we drag a handle to the other side of another
        # e.g. the top left becomes the bottom left
        if t < b:
            self.handles['in_tl'], self.handles['in_bl'] = self.handles['in_bl'], self.handles['in_tl']
            self.handles['in_tr'], self.handles['in_br'] = self.handles['in_br'], self.handles['in_tr']
            self.start_click_limits[0], self.start_click_limits[2] = self.start_click_limits[2], self.start_click_limits[0]

        if r < l:
            self.handles['in_tl'], self.handles['in_tr'] = self.handles['in_tr'], self.handles['in_tl']
            self.handles['in_bl'], self.handles['in_br'] = self.handles['in_br'], self.handles['in_bl']
            self.start_click_limits[1], self.start_click_limits[3] = self.start_click_limits[3], self.start_click_limits[1]

        # this is for when the outside part is resized
        ring_frac = (r - l) / new_full_width

        # need to use the circle values here

        c_y, c_x = self.get_centre()
        r_y, r_x = self.get_radii()

        self.make_buffers_ring(c_x, c_y, r_x, r_y, ring_frac)

    def make_buffers(self, centre_x, centre_y, outer_radius_x, outer_radius_y, inner_radius_frac):
        self.make_buffers_circle(centre_x, centre_y, outer_radius_x, outer_radius_y, False)
        self.make_buffers_ring(centre_x, centre_y, outer_radius_x, outer_radius_y, inner_radius_frac)

    def make_buffers_ring(self, centre_x, centre_y, outer_radius_x, outer_radius_y, inner_radius_frac):
        # Need to go from radii to top, left, bottom, right
        inner_radius_x = outer_radius_x * inner_radius_frac
        inner_radius_y = outer_radius_y * inner_radius_frac

        t = centre_y + inner_radius_y
        l = centre_x - inner_radius_x
        b = centre_y - inner_radius_y
        r = centre_x + inner_radius_x

        self.handles['in_tl'].set_position(l, t)
        self.handles['in_tr'].set_position(r, t)
        self.handles['in_br'].set_position(r, b)
        self.handles['in_bl'].set_position(l, b)

        self.circle.ring_frac = inner_radius_frac

        lims = self.limits
        self.signal_ring_changed.emit(lims[0], lims[1], lims[2], lims[3], inner_radius_frac)

    def set_radius_inner_fraction(self, r_x, r_y=None, frac=0.0):
        if frac >= 1 or frac < 0:
            return

        if r_y is None:
            r_y = r_x

        c_x, c_y = self.get_centre()
        r_x, r_y = self.get_radii()

        self.make_buffers(c_x, c_y, r_x, r_y, frac)
