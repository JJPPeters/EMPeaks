import OpenGL.GL as gl

from .opengl_image_tile_technique import OglImageTileTechnique
from PyQt5.QtWidgets import QOpenGLWidget

import numpy as np


class OglImageTechnique:

    def __init__(self, z_value=1, visible=True):
        self._parent = None

        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.techniques = []

        self._visible = visible

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    @property
    def parent(self: QOpenGLWidget):
        return self._parent

    @parent.setter
    def parent(self, p: QOpenGLWidget):
        self._parent = p
        for t in self.techniques:
            t.parent = p

    def initialise(self):
        for t in self.techniques:
            t.initialise()

    def on_click(self, pos_x, pos_y, ratio):
        return None

    def make_buffers(self, image, correction=0.5):
        # need to split image up depending in max texture
        max_tex_size = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)

        width = image.shape[1]
        height = image.shape[0]

        self.limits[0] = height - correction
        self.limits[1] = 0 - correction
        self.limits[2] = 0 - correction
        self.limits[3] = width - correction

        h_sections = np.ceil(image.shape[1] / max_tex_size).astype(np.int)
        v_sections = np.ceil(image.shape[0] / max_tex_size).astype(np.int)

        h_split = np.array_split(image.astype(np.float32), h_sections, axis=1)
        h_offset = 0

        image_min = np.min(image)
        image_max = np.max(image) - image_min

        self.techniques.clear()

        for h_im in h_split:

            hv_split = np.array_split(h_im, v_sections, axis=0)

            v_offset = 0

            for hv_im in hv_split:
                technique = OglImageTileTechnique(z_value=self.z_value, visible=self.visible)
                technique.make_buffers(hv_im, h_offset, v_offset, correction=correction, image_min=image_min, image_max=image_max)
                technique.parent = self.parent
                self.techniques.append(technique)

                v_offset += hv_im.shape[0]

            h_offset += h_im.shape[1]

    def render(self, projection, width, height, ratio):
        for tile in self.techniques:
            tile.render(projection, width, height, ratio)

    def set_colour_map(self, col_map):
        for tile in self.techniques:
            tile.colour_map = col_map / 255

    def set_bcg(self, b, c, g):
        bb = 1.5 - (b * 2)
        cc = 5 ** (4 * (c - 0.5))
        gg = 10 ** (4 * (-g + 0.5))

        bcg = np.array([bb, cc, gg])
        for tile in self.techniques:
            tile.bcg = bcg

    def set_levels(self, levels):
        for tile in self.techniques:
            tile.min = levels[0]
            tile.max = levels[1] - levels[0]

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, v):
        for technique in self.techniques:
            technique.visible = v
