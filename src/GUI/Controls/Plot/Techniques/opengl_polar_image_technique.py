import OpenGL.GL as gl

from .opengl_polar_image_tile_technique import OglPolarImageTileTechnique

import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget

class OglPolarImageTechnique:

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

    def make_buffers(self, angles, magnitude, alpha=None):
        # need to split image up depending in max texture
        try:
            max_tex_size = gl.glGetIntegerv(gl.GL_MAX_TEXTURE_SIZE)
        except gl.GLError:
            # this is the minimum required by OpenGL 3.0
            max_tex_size = 1024

        width = angles.shape[1]
        height = angles.shape[0]

        self.limits[0] = height
        self.limits[1] = 0
        self.limits[2] = 0
        self.limits[3] = width

        h_sections = np.ceil(angles.shape[1] / max_tex_size).astype(np.int)
        v_sections = np.ceil(angles.shape[0] / max_tex_size).astype(np.int)

        h_ang_split = np.array_split(angles.astype(np.float32), h_sections, axis=1)
        h_mag_split = np.array_split(magnitude.astype(np.float32), h_sections, axis=1)
        if alpha is not None:
            h_alpha_split = np.array_split(alpha.astype(np.float32), h_sections, axis=1)
        else:
            h_alpha_split = np.ones_like(h_ang_split, dtype=np.float32)

        h_offset = 0

        image_min = np.min(magnitude)
        image_max = np.max(magnitude) - image_min

        self.techniques.clear()

        for h_ang, h_mag, h_alpha in zip(h_ang_split, h_mag_split, h_alpha_split):

            hv_ang_split = np.array_split(h_ang, v_sections, axis=0)
            hv_mag_split = np.array_split(h_mag, v_sections, axis=0)

            hv_alpha_split = np.array_split(h_alpha, v_sections, axis=0)

            v_offset = 0

            for hv_ang, hv_mag, hv_alpha in zip(hv_ang_split, hv_mag_split, hv_alpha_split):
                technique = OglPolarImageTileTechnique(z_value=self.z_value, visible=self.visible)
                technique.make_buffers(hv_ang, hv_mag, hv_alpha, h_offset, v_offset, image_min=image_min, image_max=image_max)
                technique.parent = self.parent
                self.techniques.append(technique)

                v_offset += hv_ang.shape[0]

            h_offset += h_ang.shape[1]

    def render(self, projection, width, height, ratio):
        for tile in self.techniques:
            tile.render(projection, width, height, ratio)

    def set_colour_map(self, col_map):
        for tile in self.techniques:
            tile.colour_map = col_map / 255

    def set_levels(self, levels):
        for tile in self.techniques:
            tile.min = levels[0]
            tile.max = levels[1] - levels[0]

    def set_cmap_angle_offset(self, angle):
        angle = np.deg2rad(angle)

        for tile in self.techniques:
            tile.angle_offset = angle

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, v):
        for technique in self.techniques:
            technique.visible = v
