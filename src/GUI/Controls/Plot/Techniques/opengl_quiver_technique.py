import OpenGL.GL as gl
import numpy as np

from .opengl_technique import OglTechnique
from .opengl_attribute_buffer import OglAttributeBuffer
from .shaders import quiver_shaders as shaders

class OglQuiverTechnique(OglTechnique):

    def __init__(self, line_width=5, head_width=16, head_length=16, scale=1.0,
                 border_width=0.0, border_colour=np.array([1, 1, 1, 1]),
                 z_value=1, visible=True):
        super(OglQuiverTechnique, self).__init__()

        self.deferred_make_buffer = False

        self.deferred_positions = None
        self.deferred_lengths = None
        self.deferred_angles = None

        self.visible = visible

        self.position_buffer_location = None
        self.length_buffer_location = None
        self.angle_buffer_location = None

        # self.fill_colour_location = None
        self.border_colour_location = None

        self.expand_location = None
        self.line_width_location = None
        self.head_width_location = None
        self.head_length_location = None
        self.colourmap_location = None
        self.scale_location = None

        self.min_length_location = None
        self.max_length_location = None

        self.width_location = None
        self.height_location = None

        self.position_buffer = None
        self.length_buffer = None
        self.angle_buffer = None

        self.z_location = None
        if z_value < 1:
            z_value = 1
        elif z_value > 999:
            z_value = 999
        self.z_value = z_value

        if head_width < line_width:
            head_width = line_width

        self.expand = float(border_width)

        self.head_width = float(head_width)
        self.head_length = float(head_length)
        self.line_width = float(line_width)
        self.scale = float(scale)

        self.max_length = float(1)
        self.min_length = float(0)

        # self.fill_colour = fill_colour.astype(np.float32)
        self.border_colour = border_colour.astype(np.float32)

        # this is inflexible and only works for evently space colours maps
        c_pos = [0.0, 0.25, 0.5, 0.75, 1.0]

        c_col = np.array([[0, 140, 255, 255],
                          [65, 194, 0, 255],
                          [255, 115, 0, 255],
                          [129, 0, 194, 255],
                          [0, 140, 255, 255]])

        xx, yy = np.mgrid[0:4:256j, 0:3:4j]
        yy = yy.astype(int)

        xxf = np.floor(xx).astype(int)
        xxc = np.ceil(xx).astype(int)
        xxr = xx - xxf

        self.colour_map = c_col[xxf, yy] * (1 - xxr) + c_col[xxc, yy] * xxr
        self.colour_map /= 255

        self.limits = np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    def initialise(self):
        super(OglQuiverTechnique, self).initialise()

        vertex_shader_string = shaders.vertex_shader
        self.compile_shader(gl.GL_VERTEX_SHADER, vertex_shader_string)

        geometry_shader_string = shaders.geometry_shader
        self.compile_shader(gl.GL_GEOMETRY_SHADER, geometry_shader_string)

        fragment_shader_string = shaders.fragment_shader
        self.compile_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_string)

        self.finalise()

        self.projection_location = self.get_uniform_location("projection")
        self.z_location = self.get_uniform_location("z_value")

        # self.fill_colour_location = self.get_uniform_location("fill_colour")
        self.border_colour_location = self.get_uniform_location("border_colour")

        self.expand_location = self.get_uniform_location("expand")
        self.line_width_location = self.get_uniform_location("line_width")
        self.head_width_location = self.get_uniform_location("head_width")
        self.head_length_location = self.get_uniform_location("head_length")
        self.scale_location = self.get_uniform_location("scale")

        self.min_length_location = self.get_uniform_location("min_length")
        self.max_length_location = self.get_uniform_location("max_length")

        self.width_location = self.get_uniform_location("window_width")
        self.height_location = self.get_uniform_location("window_height")

        self.colourmap_location = self.get_uniform_location("colour_map")

        self.position_buffer_location = self.get_attribute_location("PosBuf")
        self.angle_buffer_location = self.get_attribute_location("AngBuf")
        self.length_buffer_location = self.get_attribute_location("LenBuf")

        if self.deferred_make_buffer:
            self._make_buffers()
            self.deferred_make_buffer = False

    def make_buffers(self, positions_yx, lengths, angles):
        self.limits[0] = np.max(positions_yx[:, 0])
        self.limits[1] = np.min(positions_yx[:, 1])
        self.limits[2] = np.min(positions_yx[:, 0])
        self.limits[3] = np.max(positions_yx[:, 1])

        self.min_length = 0
        self.max_length = 1

        self.deferred_positions = positions_yx
        self.deferred_lengths = lengths
        self.deferred_angles = angles

        try:
            self._make_buffers()
        except Exception as e:
            self.deferred_make_buffer = True

    def _make_buffers(self):

        if self.position_buffer_location is None:
            raise Exception("Buffer positions are invalid")

        self.position_buffer = OglAttributeBuffer(self.deferred_positions.astype(np.float32), self.position_buffer_location)
        self.length_buffer = OglAttributeBuffer(self.deferred_lengths.astype(np.float32), self.length_buffer_location)
        self.angle_buffer = OglAttributeBuffer(self.deferred_angles.astype(np.float32), self.angle_buffer_location)

        self.deferred_make_buffer = False
        self.deferred_positions = None
        self.deferred_lengths = None
        self.deferred_angles = None

    def render(self, projection, width, height, ratio):
        if self.position_buffer is None or not self.visible:
            return

        self.enable()

        self.set_projection(projection)

        gl.glUniform1f(self.z_location, self.z_value)

        gl.glUniform1f(self.line_width_location, self.line_width)
        gl.glUniform1f(self.head_width_location, self.head_width)
        gl.glUniform1f(self.head_length_location, self.head_length)
        gl.glUniform1f(self.expand_location, self.expand)
        gl.glUniform1f(self.scale_location, self.scale)

        gl.glUniform1f(self.min_length_location, self.min_length)
        gl.glUniform1f(self.max_length_location, self.max_length)

        # gl.glUniform4fv(self.fill_colour_location, 1, self.fill_colour)
        gl.glUniform4fv(self.border_colour_location, 1, self.border_colour)

        gl.glUniform1i(self.width_location, width)
        gl.glUniform1i(self.height_location, height)

        gl.glUniform4fv(self.colourmap_location, 256, self.colour_map)

        self.position_buffer.bind()
        self.length_buffer.bind()
        self.angle_buffer.bind()

        gl.glDrawArrays(gl.GL_POINTS, 0, self.position_buffer.size)

        self.position_buffer.unbind()
        self.length_buffer.unbind()
        self.angle_buffer.unbind()

        self.disable()
