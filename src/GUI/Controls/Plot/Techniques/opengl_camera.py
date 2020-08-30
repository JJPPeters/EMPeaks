from .opengl_camera_pipeline import OglCameraPipeline
import numpy as np
import OpenGL.GL as gl


class OglCamera(OglCameraPipeline):
    def __init__(self, invert_y=False):
        super(OglCamera, self).__init__(invert_y)

        self.pixel_ratio = 1.0
        self.aspect_ratio = 1

    def set_width_height(self, width, height):
        aspect_new = width / height

        w = self.projection_edges[3] - self.projection_edges[1]
        h = self.projection_edges[0] - self.projection_edges[2]

        # special case for when the aspect ratio crosses 1
        if aspect_new <= 1 and self.aspect_ratio >= 1:
            w = h
        elif aspect_new > 1 and self.aspect_ratio <= 1:
            h = w

        self.aspect_ratio = aspect_new

        if aspect_new <= 1:
            view_width = w
            view_height = view_width / aspect_new
        else:
            view_height = h
            view_width = view_height * aspect_new

        dw = view_width / 2
        dh = view_height / 2

        centre_w = (self.projection_edges[3] + self.projection_edges[1]) / 2
        centre_h = (self.projection_edges[0] + self.projection_edges[2]) / 2

        self.projection_edges[0] = centre_h + dh
        self.projection_edges[1] = centre_w - dw
        self.projection_edges[2] = centre_h - dh
        self.projection_edges[3] = centre_w + dw

    def mouse_position(self, pos_xy, use_image_zero=True):
        w = self.projection_edges[3] - self.projection_edges[1]
        h = self.projection_edges[0] - self.projection_edges[2]

        px = pos_xy[0] * w
        py = pos_xy[1] * h

        if use_image_zero:
            px += self.projection_edges[1]
            py += self.projection_edges[2]

        return px, py

    def mouse_pan(self, dx, dy, width, height):
        if dx == 0.0 and dy == 0.0:
            return

        h = self.projection_edges[0] - self.projection_edges[2]
        w = self.projection_edges[3] - self.projection_edges[1]

        x_scaling = w / width
        y_scaling = h / height

        dx = dx * x_scaling
        dy = dy * y_scaling

        self.projection_edges[0] -= dy * self.yf
        self.projection_edges[1] -= dx
        self.projection_edges[2] -= dy * self.yf
        self.projection_edges[3] -= dx

    def mouse_stretch_from_origin(self, dx, dy, width, height):
        if dx == 0.0 and dy == 0.0:
            return

        h = self.projection_edges[0] - self.projection_edges[2]
        w = self.projection_edges[3] - self.projection_edges[1]

        x_scaling = w / width
        y_scaling = h / height

        dx = dx * x_scaling
        dy = dy * y_scaling

        if self.invert_y:
            self.projection_edges[0] += dy
        else:
            self.projection_edges[0] -= dy

        self.projection_edges[3] -= dx

    def mouse_scroll(self, d, pos_xy):
        # d is positive for scrolling up (zooming in)
        # pos_xy is the fractional position to preserve the position off (i.e. the mouse position)

        w = self.projection_edges[3] - self.projection_edges[1]
        h = self.projection_edges[0] - self.projection_edges[2]

        aspect = w / h

        scaling = 1.0 * np.max((w, h)) / 1000
        lim = 5
        ds = d * scaling

        if aspect > 1:
            new_w = w - ds
            if new_w < lim:
                new_w = lim

            new_h = new_w / aspect
        else:
            new_h = h - ds
            if new_h < lim:
                new_h = lim

            new_w = new_h * aspect

        l = self.projection_edges[1] + w * pos_xy[0] - new_w * pos_xy[0]
        r = l + new_w

        b = self.projection_edges[2] + h * pos_xy[1] - new_h * pos_xy[1]
        t = b + new_h

        self.set_projection_limits(t, l, b, r)

    def scroll_width(self, d, pos):
        w = self.projection_edges[3] - self.projection_edges[1]
        h = self.projection_edges[0] - self.projection_edges[2]

        scaling = 1.0 * np.max((w, h)) / 1000
        lim = 5
        ds = d * scaling

        new_w = w - ds
        if new_w < lim:
            new_w = lim

        l = self.projection_edges[1] + w * pos - new_w * pos
        r = l + new_w

        t = self.projection_edges[0]
        b = self.projection_edges[2]

        self.set_projection_limits(t, l, b, r)

    def scroll_height(self, d, pos):
        # pos is fractional, invert if axis is inverted too

        if self.invert_y:
            pos = 1 - pos

        w = self.projection_edges[3] - self.projection_edges[1]
        h = self.projection_edges[0] - self.projection_edges[2]

        scaling = 1.0 * np.max((w, h)) / 1000
        lim = 5
        ds = d * scaling

        new_h = h - ds
        if new_h < lim:
            new_h = lim

        b = self.projection_edges[2] + h * pos - new_h * pos
        t = b + new_h

        l = self.projection_edges[1]
        r = self.projection_edges[3]

        self.set_projection_limits(t, l, b, r)