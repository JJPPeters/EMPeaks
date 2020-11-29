import OpenGL.GL as gl

from PyQt5.QtWidgets import QOpenGLWidget
from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .opengl_texture_buffer import OglTextureBuffer
from .shaders import polar_image_shaders as shaders

import numpy as np


class OglPolarImageTileTechnique(OglTechnique):

    def __init__(self,
                 pixel_scale=1.0,
                 origin=np.array([0.0, 0.0], dtype=np.float32),
                 z_value=1, visible=True):
        super(OglPolarImageTileTechnique, self).__init__()

        self.deferred_make_buffer = False
        self.deferred_angle = None
        self.deferred_magnitude = None
        self.deferred_alpha = None

        self.coord_buffer_location = None
        self.rectangle_buffer_location = None

        self.angle_buffer = None
        self.magnitude_buffer = None
        self.alpha_buffer = None
        self.coord_buffer = None
        self.rectangle_buffer = None

        self.min_location = None
        self.max_location = None
        self.angle_offset_location = None

        self.colourmap_location = None
        self.texture_angle_location = None
        self.texture_magnitude_location = None
        self.texture_alpha_location = None

        self.z_location = None
        self.scale_location = None
        self.origin_location = None

        self.min = 0.0
        self.max = 1.0

        self.angle_offset = 0

        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.visible = visible

        self.image_size = np.array([0.0, 0.0], dtype=np.float32)
        self.pixel_scale = float(pixel_scale)
        self.origin = origin.astype(np.float32)

        self.colour_map = np.zeros((256, 4), dtype=np.float32)
        self.colour_map[:, 0] = np.linspace(0, 1, 256)
        self.colour_map[:, 1] = np.linspace(0, 1, 256)
        self.colour_map[:, 2] = np.linspace(0, 1, 256)
        self.colour_map[:, 3] = 1

    @property
    def limits(self: QOpenGLWidget):
        limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        limits[0] = (self.image_size[0] * self.pixel_scale) - self.origin[0]
        limits[1] = 0 - self.origin[1]
        limits[2] = 0 - self.origin[0]
        limits[3] = (self.image_size[1] * self.pixel_scale) - self.origin[1]

        return limits

    def initialise(self):
        if self.texture_angle_location is not None:
            return

        super(OglPolarImageTileTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")

        self.z_location = self.get_uniform_location("z_value")
        self.origin_location = self.get_uniform_location("origin")
        self.scale_location = self.get_uniform_location("scale")

        self.min_location = self.get_uniform_location("magnitude_min")
        self.max_location = self.get_uniform_location("magnitude_max")
        self.angle_offset_location = self.get_uniform_location("angle_offset")

        self.colourmap_location = self.get_uniform_location("colour_map")

        self.texture_angle_location = self.get_uniform_location("tex_unit_angle")
        self.texture_magnitude_location = self.get_uniform_location("tex_unit_magnitude")
        self.texture_alpha_location = self.get_uniform_location("tex_unit_alpha")

        self.rectangle_buffer_location = self.get_attribute_location("rectangle_position")
        self.coord_buffer_location = self.get_attribute_location("tex_coords")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, angle, magnitude, alpha=None, h_o=0, v_o=0, pixel_scale=1.0, image_min=None, image_max=None):
        # first we need to get a buffer of intensities
        if image_min is None:
            self.min = np.min(magnitude)
        else:
            self.min = image_min

        if image_max is None:
            self.max = np.max(magnitude) - self.min
        else:
            self.max = image_max

        self.image_size[0] = angle.shape[0]
        self.image_size[1] = angle.shape[1]
        self.pixel_scale = float(pixel_scale)
        self.origin = np.array([v_o, h_o], dtype=np.float32)

        self.deferred_angle = angle
        self.deferred_magnitude = magnitude
        self.deferred_alpha = alpha

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):
        t = self.image_size[0]
        l = 0
        b = 0
        r = self.image_size[1]

        positions = np.array([[l, b],
                              [r, b],
                              [r, t],
                              [r, t],
                              [l, t],
                              [l, b]], dtype=np.float32)

        coords = np.array([[0, 0],
                           [1, 0],
                           [1, 1],
                           [1, 1],
                           [0, 1],
                           [0, 0]], dtype=np.float32)

        if self.rectangle_buffer_location is None or self.coord_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        self.angle_buffer = OglTextureBuffer(self.deferred_angle.astype(np.float32), unit=0)
        self.magnitude_buffer = OglTextureBuffer(self.deferred_magnitude.astype(np.float32), unit=1)
        if self.deferred_alpha is not None:
            self.alpha_buffer = OglTextureBuffer(self.deferred_alpha.astype(np.float32), unit=2)
        else:
            self.alpha_buffer = OglTextureBuffer(np.ones_like(self.deferred_angle, dtype=np.float32), unit=2)
        self.coord_buffer = OglAttributeBuffer(coords, self.coord_buffer_location)
        self.rectangle_buffer = OglAttributeBuffer(positions, self.rectangle_buffer_location)

        # I don't want to store these!
        self.deferred_magnitude = None
        self.deferred_angle = None
        self.deferred_alpha = None
        self.deferred_make_buffer = False

    def render(self, projection, width, height, ratio):
        if not self.visible:
            return

        if self.angle_buffer is None or self.magnitude_buffer is None \
                or self.rectangle_buffer is None or self.coord_buffer is None:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform1f(self.scale_location, self.pixel_scale)
        gl.glUniform2fv(self.origin_location, 1, self.origin)

        gl.glUniform1f(self.min_location, self.min)
        gl.glUniform1f(self.max_location, self.max)
        gl.glUniform1f(self.angle_offset_location, self.angle_offset)

        gl.glUniform1i(self.texture_angle_location, self.angle_buffer.unit)
        gl.glUniform1i(self.texture_magnitude_location, self.magnitude_buffer.unit)
        gl.glUniform1i(self.texture_alpha_location, self.alpha_buffer.unit)

        gl.glUniform4fv(self.colourmap_location, 256, self.colour_map)

        self.angle_buffer.bind()
        self.magnitude_buffer.bind()
        self.alpha_buffer.bind()
        self.rectangle_buffer.bind()
        self.coord_buffer.bind()

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.rectangle_buffer.size)

        self.angle_buffer.unbind()
        self.magnitude_buffer.unbind()
        self.alpha_buffer.unbind()
        self.rectangle_buffer.unbind()
        self.coord_buffer.unbind()

        self.disable()
