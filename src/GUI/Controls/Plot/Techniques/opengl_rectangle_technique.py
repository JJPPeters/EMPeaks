import OpenGL.GL as gl

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .shaders import rectangle_shaders as shaders

import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget

class OglRectangleTechnique(OglTechnique):

    def __init__(self, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2,
                 z_value=1, visible=True):
        super(OglRectangleTechnique, self).__init__()

        self.deferred_make_buffer = False

        self.visible = visible

        self.fill_colour_location = None
        self.border_colour_location = None
        self.width_location = None
        self.height_location = None
        self.border_width_location = None

        self.rectangle_buffer_location = None
        self.coord_buffer_location = None

        self.coord_buffer = None
        self.rectangle_buffer = None

        self.z_location = None
        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

        self.fill_colour = fill_colour.astype(np.float32)
        self.border_colour = border_colour.astype(np.float32)
        self.border_width = float(border_width)

    def initialise(self):
        if self.coord_buffer_location is not None or self.parent is None:
            return

        super(OglRectangleTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")

        self.z_location = self.get_uniform_location("z_value")

        self.fill_colour_location = self.get_uniform_location("fill_colour")
        self.border_colour_location = self.get_uniform_location("border_colour")
        self.width_location = self.get_uniform_location("width")
        self.height_location = self.get_uniform_location("height")
        self.border_width_location = self.get_uniform_location("border_width")

        self.rectangle_buffer_location = self.get_attribute_location("rectangle_position")
        self.coord_buffer_location = self.get_attribute_location("rectangle_limits")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, t, l, b, r):
        self.limits[0] = t
        self.limits[1] = l
        self.limits[2] = b
        self.limits[3] = r

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):
        if self.rectangle_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        t = self.limits[0]
        l = self.limits[1]
        b = self.limits[2]
        r = self.limits[3]

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

        self.rectangle_buffer = OglAttributeBuffer(positions.astype(np.float32), self.rectangle_buffer_location)
        self.coord_buffer = OglAttributeBuffer(coords.astype(np.float32), self.coord_buffer_location)

    def update_buffers(self, t, l, b, r):
        if self.rectangle_buffer is None:
            self.make_buffers(t, l, b, r)
            return

        self.limits[0] = t
        self.limits[1] = l
        self.limits[2] = b
        self.limits[3] = r

        positions = np.array([[l, b],
                              [r, b],
                              [r, t],
                              [r, t],
                              [l, t],
                              [l, b]], dtype=np.float32)

        self.rectangle_buffer.update_all(positions.astype(np.float32))

    def render(self, projection, width, height, ratio):
        if self.rectangle_buffer is None or not self.visible:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform4fv(self.fill_colour_location, 1, self.fill_colour)
        gl.glUniform4fv(self.border_colour_location, 1, self.border_colour)
        gl.glUniform1f(self.border_width_location, self.border_width)

        gl.glUniform1f(self.width_location, ratio[0] * (self.limits[3] - self.limits[1]))
        gl.glUniform1f(self.height_location, ratio[1] * (self.limits[0] - self.limits[2]))

        self.rectangle_buffer.bind()
        self.coord_buffer.bind()

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.rectangle_buffer.size)

        self.rectangle_buffer.unbind()
        self.coord_buffer.unbind()

        self.disable()
