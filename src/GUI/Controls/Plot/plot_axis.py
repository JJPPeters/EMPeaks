from PyQt5 import QtCore, QtGui
from GUI.Controls.Plot.Plottables import LinePlot, TextPlot, NumberTextPlot
from .Techniques import VerticalAlign, HorizontalAlign

from GUI.Controls.Plot.Techniques import OglNumberTextTechnique

import numpy as np
from math import floor, ceil, log10
from enum import Enum

class AxisLocation(Enum):
    Top = 0
    Left = 1
    Bottom = 2
    Right = 3

class Axis:
    def __init__(self, parent, location, line_width=2, colour=np.array([1.0,1.0,1.0,1.0], dtype=np.float32)):
        self.line_width = line_width
        self.colour = colour

        # TODO: set start and end properly
        self.start_value = 0.0
        self.finish_value = 1.0

        self.parent = parent

        self.axis_location = location

        self.show_labels = self.axis_location == AxisLocation.Left or self.axis_location == AxisLocation.Bottom
        self.show_axis_label = self.show_labels

        #
        # Mouse dragging stuff!
        #

        self.mouse_down_pos = None
        self.mouse_last_pos = None
        self.mouse_is_dragging = False
        self.mouse_drag_modifiers = None

        #
        # OpenGL stuff
        #

        self.target_tick_count = 5
        self.minor_ticks = 1

        self.major_tick_length_px = 5
        self.minor_tick_length_px = 2.5
        self.tick_count = self.target_tick_count * 2

        self.axis_line = LinePlot(points=None, thickness=line_width, colour=colour, z_value=999, visible=True)
        self.major_lines = []
        self.minor_lines = []

        self.tick_labels = []

        for i in range(self.tick_count):
            self.major_lines.append(LinePlot(thickness=line_width, colour=colour, z_value=999, visible=True))
            if self.show_labels:
                if self.axis_location == AxisLocation.Left:
                    self.tick_labels.append(NumberTextPlot(horizontal_align=HorizontalAlign.Right, vertical_align=VerticalAlign.Middle, z_value=999))
                elif self.axis_location == AxisLocation.Bottom:
                    self.tick_labels.append(NumberTextPlot(horizontal_align=HorizontalAlign.Centre, vertical_align=VerticalAlign.Top, z_value=999))

        self.axis_label = TextPlot("Test units", 0, 0, fontsize=70, colour=colour, z_value=999)

        self.exponent_label = None
        if self.axis_location == AxisLocation.Left:
            self.exponent_label = NumberTextPlot(horizontal_align=HorizontalAlign.Centre, vertical_align=VerticalAlign.Middle, font_size=50, z_value=999)
        elif self.axis_location == AxisLocation.Bottom:
            self.exponent_label = NumberTextPlot(horizontal_align=HorizontalAlign.Centre, vertical_align=VerticalAlign.Bottom, font_size=50, z_value=999)

        if self.axis_location == AxisLocation.Left:
            self.axis_label.set_rotation(90)
            # for tl in self.tick_labels:
            #     tl.set_rotation(90)
        elif self.axis_location == AxisLocation.Left:
            self.axis_label.set_rotation(270)

        self.draw_points = None
        self.update_positions()

    def update_positions(self):
        self.draw_points = None
        label_correction = np.array([0,0], dtype=np.float32)
        if self.axis_location == AxisLocation.Top:
            self.draw_points = np.array([[self.parent.top_border_position, self.parent.left_border_position],
                                         [self.parent.top_border_position, self.parent.right_border_position]], dtype=np.float32)
            label_correction[0] = -40
        elif self.axis_location == AxisLocation.Left:
            self.draw_points = np.array([[self.parent.top_border_position, self.parent.left_border_position],
                                         [self.parent.bottom_border_position, self.parent.left_border_position]], dtype=np.float32)
            label_correction[1] = -40
        elif self.axis_location == AxisLocation.Bottom:
            self.draw_points = np.array([[self.parent.bottom_border_position, self.parent.left_border_position],
                                         [self.parent.bottom_border_position, self.parent.right_border_position]], dtype=np.float32)
            label_correction[0] = 40
        elif self.axis_location == AxisLocation.Right:
            self.draw_points = np.array([[self.parent.top_border_position, self.parent.right_border_position],
                                         [self.parent.bottom_border_position, self.parent.right_border_position]], dtype=np.float32)
            label_correction[1] = 40

        self.axis_line.make_buffers(self.draw_points)

        # set the position of the axis label (aka in middle + correction)
        mid = np.mean(self.draw_points, axis=0) + label_correction
        self.axis_label.set_position(mid)

        # set the exponent label (aka at the end of the axis + correction)
        if self.axis_location in [AxisLocation.Left, AxisLocation.Right]:
            end = self.draw_points[0, :] + label_correction
        else:
            end = self.draw_points[1, :] + label_correction

        if self.exponent_label is not None:
            self.exponent_label.set_position(end)

    def get_draw_range(self):
        if self.axis_location == AxisLocation.Top or self.axis_location == AxisLocation.Bottom:
            return abs(self.draw_points[1,1] - self.draw_points[0, 1])
        else:
            return abs(self.draw_points[1,0] - self.draw_points[0,0])

    def get_draw_border(self):
        if self.axis_location == AxisLocation.Top or self.axis_location == AxisLocation.Bottom:
            return self.draw_points[0, 0]
        else:
            return self.draw_points[1, 1]

    def get_draw_origin(self):
        if self.axis_location == AxisLocation.Top or self.axis_location == AxisLocation.Bottom:
            return np.min(self.draw_points[:,1])
        else:
            return np.min(self.draw_points[:,0])

    def set_tick_positions(self, limits):

        if self.axis_location == AxisLocation.Top or self.axis_location == AxisLocation.Bottom:
            new_start = limits[1]
            new_finish = limits[3]
        elif self.axis_location == AxisLocation.Left or self.axis_location == AxisLocation.Right:
            # if self.parent.plot_view.view_camera.invert_y:
            #     new_start = limits[0]
            #     new_finish = limits[2]
            # else:
            new_start = limits[2]
            new_finish = limits[0]
        else:
            return

        # This small optimisation cancels stuff like rescaling the tick lengths when resizing
        # It could be semi reimplemented by having a function to recalculate the tick positions when needed
        # if new_start == self.start_value and new_finish == self.finish_value:
        #     return

        self.start_value = new_start
        self.finish_value = new_finish

        # rr = self.end - self.start
        rr = self.finish_value - self.start_value

        # get nearest (floored) power of 10
        pow_ten = floor(log10(abs(rr)))
        r = rr / (10**pow_ten)

        if self.exponent_label is not None:
            if pow_ten == 0:
                self.exponent_label.set_text("")
            else:
                self.exponent_label.set_text("×10" + self.exponent_label.number_to_superscript(str(pow_ten)))

        step = r / self.target_tick_count

        remain_100 = abs(step - 1)
        remain_025 = abs(step - 0.25)
        remain_050 = abs(step - 0.5)

        step_size = 0

        str_fmt = None

        if remain_100 < remain_025 and remain_100 < remain_050:
            step_size = 1 * 10**pow_ten
            str_fmt = '{0:.0f}'
        elif remain_025 < remain_100 and remain_025 < remain_050:
            step_size = 0.25 * 10**pow_ten
            str_fmt = '{0:.2f}'
        elif remain_050 < remain_025 and remain_050 < remain_100:
            step_size = 0.5 * 10**pow_ten
            str_fmt = '{0:.1f}'

        tick_start = step_size * ceil(self.start_value / step_size)

        tick_positions = []
        tick_text = []

        pos = tick_start
        while pos <= self.finish_value:
            # position as a fraction of the axes
            pos_frac = (pos - self.start_value) / rr

            if self.parent.plot_view.view_camera.invert_y:
                pos_frac = 1 - pos_frac
            # position as a fraction of the plot display
            pos_frac = self.get_draw_origin() + pos_frac * self.get_draw_range()

            tick_positions.append(pos_frac)


            tick_text.append( str_fmt.format(pos / 10**pow_ten) )
            pos += step_size

        # TODO: I'm hoping there will be a maximum limit on the number of ticks needed, so add a few here in case we have squoze in an extra one or two
        if len(self.major_lines) < len(tick_positions):
            for i in range(len(tick_positions) - len(self.major_lines)):
                self.major_lines.append(LinePlot(thickness=self.line_width, colour=self.colour, z_value=999, visible=True))
                self.major_lines[-1].initialise()

                if self.show_labels:
                    if self.axis_location == AxisLocation.Left:
                        self.tick_labels.append(
                            NumberTextPlot(horizontal_align=HorizontalAlign.Right, vertical_align=VerticalAlign.Middle,
                                           z_value=999))
                    elif self.axis_location == AxisLocation.Bottom:
                        self.tick_labels.append(
                            NumberTextPlot(horizontal_align=HorizontalAlign.Centre, vertical_align=VerticalAlign.Top,
                                           z_value=999))
                    self.tick_labels[-1].initialise()

        positions = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float32)

        c = 0
        for tp, tt in zip(tick_positions, tick_text):

            if self.axis_location == AxisLocation.Top:
                positions[0, 0] = self.get_draw_border()
                positions[1, 0] = positions[0, 0] + self.major_tick_length_px
                positions[:, 1] = tp
            elif self.axis_location == AxisLocation.Bottom:
                positions[0, 0] = self.get_draw_border()
                positions[1, 0] = positions[0, 0] - self.major_tick_length_px
                positions[:, 1] = tp
            elif self.axis_location == AxisLocation.Left:
                positions[0, 1] = self.get_draw_border()
                positions[1, 1] = positions[0, 1] + self.major_tick_length_px
                positions[:, 0] = tp
            elif self.axis_location == AxisLocation.Right:
                positions[0, 1] = self.get_draw_border()
                positions[1, 1] = positions[0, 1] - self.major_tick_length_px
                positions[:, 0] = tp

            self.major_lines[c].set_points(positions)
            self.major_lines[c].visible = True
            if self.show_labels:
                self.tick_labels[c].visible = True
                if self.axis_location == AxisLocation.Left:
                    self.tick_labels[c].make_buffers(positions[0,:] + np.array([0, -10]), tt, 50)
                elif self.axis_location == AxisLocation.Bottom:
                    self.tick_labels[c].make_buffers(positions[0, :] + np.array([10, 0]), tt, 50)
            c += 1

        for i in range(c, len(self.major_lines)):
            self.major_lines[i].visible = False
            if self.show_labels:
                self.tick_labels[i].visible = False

    def initialise(self):
        self.axis_line.initialise()

        for t in self.major_lines:
            t.initialise()

        if self.show_labels:
            for tl in self.tick_labels:
                tl.initialise()
            if self.exponent_label is not None:
                self.exponent_label.initialise()

        self.axis_label.initialise()

    def set_points(self, points):
        self.axis_line.set_points(points)

    def pos_in_axis_area(self, pos_x, pos_y):
        if self.axis_location == AxisLocation.Bottom:
            in_vert = pos_y > self.parent.bottom_border_position
            in_horz = self.parent.left_border_position < pos_x < self.parent.right_border_position
            return in_vert and in_horz
        elif self.axis_location == AxisLocation.Left:
            in_horz = pos_x < self.parent.left_border_position
            in_vert = self.parent.top_border_position < pos_y < self.parent.bottom_border_position
            return in_vert and in_horz

    def on_mouse_press(self, pos_x, pos_y, button, modifiers):
        if not self.pos_in_axis_area(pos_x, pos_y):
            return

        self.mouse_down_pos = (pos_x, pos_y)
        self.mouse_last_pos = (pos_x, pos_y)
        self.mouse_is_dragging = False
        self.mouse_drag_modifiers = modifiers

        return self

    def on_mouse_move(self, pos_x, pos_y, button, modifiers):
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
        if modifiers & QtCore.Qt.ControlModifier:
            if self.axis_location == AxisLocation.Bottom:
                self.parent.plot_view.on_mouse_stretch_horizontal(dx)
            elif self.axis_location == AxisLocation.Left:
                self.parent.plot_view.on_mouse_stretch_vertical(dy)
        else:
            if self.axis_location == AxisLocation.Bottom:
                self.parent.plot_view.on_mouse_pan_horizontal(dx)
            elif self.axis_location == AxisLocation.Left:
                self.parent.plot_view.on_mouse_pan_vertical(dy)

    def on_mouse_release(self, pos_x, pos_y, button, modifiers):
        # This doesnt need to do anything!
        return

    def on_mouse_scroll(self, pos_x, pos_y, delta):
        # print("THIS IS NOT IMPLEMENTED YET!")

        if not self.pos_in_axis_area(pos_x, pos_y):
            return

        if self.axis_location == AxisLocation.Bottom:
            # need the fractional position within the plot?
            frac = (pos_x - self.draw_points[0, 1]) / (self.draw_points[1, 1] - self.draw_points[0, 1])
            self.parent.plot_view.on_mouse_scroll_horizontal(delta, frac)
        if self.axis_location == AxisLocation.Left:
            # need the fractional position within the plot?
            frac = (pos_y - self.draw_points[0, 0]) / (self.draw_points[1, 0] - self.draw_points[0, 0])
            self.parent.plot_view.on_mouse_scroll_vertical(delta, frac)

        return self

    @property
    def limits(self):
        return self.axis_line.limits

    @property
    def z_value(self):
        return 999

    @property
    def visible(self):
        return True

    def render(self, projection, width, height, ratio):
        self.axis_line.render(projection, width, height, ratio)

        for t in self.major_lines:
            t.render(projection, width, height, ratio)

        if self.show_labels:
            for tl in self.tick_labels:
                tl.render(projection, width, height, ratio)
            if self.exponent_label is not None:
                self.exponent_label.render(projection, width, height, ratio)

        if self.show_axis_label:
            self.axis_label.render(projection, width, height, ratio)