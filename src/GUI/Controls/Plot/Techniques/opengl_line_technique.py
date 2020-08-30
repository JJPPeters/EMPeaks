import OpenGL.GL as gl

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .shaders import line_shaders as shaders

import numpy as np

# TODO: could initiailise with points now
class OglLineTechnique(OglTechnique):

    def __init__(self, thickness=1, colour=None, z_value=1, visible=True):
        super(OglLineTechnique, self).__init__()

        #
        # OpenGL stuff
        #

        self.deferred_make_buffer = False

        self.position_buffer_location = None
        self.colour_location = None
        self.width_location = None
        self.height_location = None
        self.line_width_location = None

        self.position_buffer = None
        self.z_location = None

        #
        # Actual data
        #

        self.points = None

        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        if colour is None:
            self.colour = np.ones((1, 4), dtype=np.float32)
            self.colour[0, 1] = 0.4
        else:
            self.colour = colour.astype(np.float32)

        self.thickness = thickness

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)
        self.visible = visible

        self.deferred_make_buffer = None

    def initialise(self):
        # check if this has been initialised
        if self.position_buffer_location is not None:
            return

        super(OglLineTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        geometry_shader_string = shaders.geometry_shader
        self.compile_shader(gl.GL_GEOMETRY_SHADER, geometry_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")

        self.z_location = self.get_uniform_location("z_value")

        self.width_location = self.get_uniform_location("window_width")
        self.height_location = self.get_uniform_location("window_height")
        self.line_width_location = self.get_uniform_location("thickness")
        self.colour_location = self.get_uniform_location("colour")

        self.position_buffer_location = self.get_attribute_location("PosBuf")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, positions_yx):
        self.points = positions_yx.astype(np.float32)

        self.limits[0] = np.max(self.points[:, 0])
        self.limits[1] = np.min(self.points[:, 1])
        self.limits[2] = np.min(self.points[:, 0])
        self.limits[3] = np.max(self.points[:, 1])

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):
        if self.position_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        if self.points is None:
            return

        if self.position_buffer is not None and self.points.shape[0] == self.position_buffer.size:
            self.position_buffer.update_all(self.points)
        else:
            self.position_buffer = OglAttributeBuffer(self.points.astype(np.float32), self.position_buffer_location)

        self.deferred_make_buffer = False

    def render(self, projection, width, height, ratio):
        if self.position_buffer is None or not self.visible:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)
        gl.glUniform4fv(self.colour_location, 1, self.colour)
        gl.glUniform1f(self.width_location, width)
        gl.glUniform1f(self.height_location, height)
        gl.glUniform1f(self.line_width_location, self.thickness)

        self.position_buffer.bind()

        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, self.position_buffer.size)

        self.position_buffer.unbind()

        self.disable()
