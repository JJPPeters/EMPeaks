import OpenGL.GL as gl

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .shaders import quadrilateral_shaders as shaders

import numpy as np
from PyQt5.QtWidgets import QOpenGLWidget

class OglQuadrilateralTechnique(OglTechnique):

    def __init__(self, fill_colour=np.zeros((4, )), border_colour=np.ones((4, )), border_width=2,
                 z_value=1, visible=True):
        super(OglQuadrilateralTechnique, self).__init__()

        self.deferred_make_buffer = False

        self.visible = visible

        self.fill_colour_location = None
        self.border_colour_location = None
        self.width_location = None
        self.height_location = None
        self.border_width_location = None

        self.quad_buffer_location = None
        self.coord_buffer_location = None

        self.coord_buffer = None
        self.quad_buffer = None

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

        self.deferred_vertices = None
        self.deferred_coords = None

    def initialise(self):
        if self.coord_buffer_location is not None or self.parent is None:
            return

        super(OglQuadrilateralTechnique, self).initialise()

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

        self.quad_buffer_location = self.get_attribute_location("rectangle_position")
        self.coord_buffer_location = self.get_attribute_location("rectangle_limits")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, p1, p2, p3, p4):

        # take the coords and put them in the right order (which is apparently anti clockwise)

        ps = np.array([p1, p2, p3, p4])

        mid = np.mean(ps, axis=0)

        angles = np.zeros(4)

        for i in range(4):
            p_rel = ps[i] - mid
            angles[i] = np.arctan2(p_rel[1], p_rel[0])# % (2 * np.pi)

        ids = np.argsort(angles)

        self.deferred_vertices = np.array([ps[ids[0], :],
                                           ps[ids[1], :],
                                           ps[ids[2], :],
                                           ps[ids[2], :],
                                           ps[ids[3], :],
                                           ps[ids[0], :]], dtype=np.float32)

        self.deferred_coords = np.array([[0, 0],
                                         [1, 0],
                                         [1, 1],
                                         [1, 1],
                                         [0, 1],
                                         [0, 0]], dtype=np.float32)

        self.limits[0] = np.max(self.deferred_vertices[:, 1])
        self.limits[1] = np.min(self.deferred_vertices[:, 0])
        self.limits[2] = np.min(self.deferred_vertices[:, 1])
        self.limits[3] = np.max(self.deferred_vertices[:, 0])

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):
        if self.quad_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        if self.quad_buffer and self.quad_buffer.size == self.deferred_vertices.shape[0]:
            self.quad_buffer.update_all(self.deferred_vertices.astype(np.float32))
            # assume coord buffer has been made!
        else:
            self.quad_buffer = OglAttributeBuffer(self.deferred_vertices.astype(np.float32), self.quad_buffer_location)
            self.coord_buffer = OglAttributeBuffer(self.deferred_coords.astype(np.float32), self.coord_buffer_location)

    def render(self, projection, width, height, ratio):
        if self.quad_buffer is None or not self.visible:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform4fv(self.fill_colour_location, 1, self.fill_colour)
        gl.glUniform4fv(self.border_colour_location, 1, self.border_colour)
        gl.glUniform1f(self.border_width_location, self.border_width)

        gl.glUniform1f(self.width_location, ratio[0] * (self.limits[3] - self.limits[1]))
        gl.glUniform1f(self.height_location, ratio[1] * (self.limits[0] - self.limits[2]))

        self.quad_buffer.bind()
        self.coord_buffer.bind()

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.quad_buffer.size)

        self.quad_buffer.unbind()
        self.coord_buffer.unbind()

        self.disable()
